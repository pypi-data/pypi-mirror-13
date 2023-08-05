import MySQLdb
import sys

class TDISQL:
	'Data structure for SQL manipulation using Python'

	"""
	Function: init
	Initializes connection to MySQL database
	Arguments:
		host: host name for the database you are connecting to
		user: username for the database
		password: corresponding password for the given username
		dbName: name of the MySQL database you want to work on
	"""
	def __init__(self, host, user, password, dbName):
		self.db = MySQLdb.connect(host, user, password, dbName)

	"""
	Parses a string containing the normal amino acid, the location and
	the mutated amino acid. The function separates these three values in the
	string and returns them in a tuple.

	@param aaCode the string containing the AA information
	@return aaTup tuple in the following form: (normal AA, AA locatin, mutated AA)
	"""
	@staticmethod
	def parseAACode(self, aaCode):

		#if there are no digits in the aaCode, then the code describes the mutation. We return null for original AA and AA loc and set AA mutation to the aaCode
		if not any(char.isdigit() for char in aaCode):
			return ("NULL", "NULL", aaCode)

		"""
		Algorithm to parse a typical AA code. Will return a tuple of the following format:
		(original AA, AA location, mutated AA). In some cases, the mutated AA may be 'fs' for frameshift.
		In other cases, the only information provided is the mutation location, in which case we return null for the AA information and only give the location.
		"""
		foundDigit = 0
		origAA = ""
		aaPos = ""
		mutAA = ""

		for char in aaCode:
			if foundDigit == 0:
				if char.isdigit():
					foundDigit = 1
					aaPos += char
				else:
					origAA += char
			elif foundDigit == 1:
				if char.isdigit():
					aaPos += char
				else:
					mutAA += char

		if origAA == "":
			origAA = "NULL"

		if aaPos == "":
			aaPos = "NULL"
		else:
			aaPos = int(aaPos)

		if mutAA == "":
			mutAA = "NULL"
		# try:
		# 	aaPos = int(aaPos)
		# except:
		# 	aaPos = "NULL"
		return (origAA, aaPos, mutAA)

	"""
	Function reads in a line from the raw input file, 
	parses out all the different data for each data field,
	then returns the data formatted for an 'SQL insert' command.

	@param splitLine Line of input text as a list of strings split by their delimiter
	@param isString List of binary values indicating whether or not the corresponding index in splitLine should be interpreted
						as a string or not.
	@param firstNull whether the first element in the insert should be 'NULL' (due to auto-incrementing the primary key)
	@return valueString Data formatted as a string for input into an 'SQL insert' command.
	"""
	def processValues(self, splitLine, isString, firstNull = True):
		valueString = ""
		if firstNull:
			valueString += "NULL"
		for i in range(len(splitLine)):
			if splitLine[i] == "null" or splitLine[i] == "NULL":
				valueString += ",NULL"
			else:
				if isString[i] == 1:
					if "'" in splitLine[i]:
						splitLine[i] = splitLine[i].replace("'", "\\'")
						#print splitLine[i]
					quotedItem = ",'" + splitLine[i] + "'"
					valueString += quotedItem
				elif isString[i] == 0:
					item = "," + str(splitLine[i])
					valueString += item
				elif isString[i] == 2:
					parsedCode = self.parseAACode(splitLine[i])
					valueString += "," + str(parsedCode[1]) + ",'" + str(parsedCode[0]) + "','" + str(parsedCode[2]) + "'" 
		return valueString

	# def exists(self, cursor, query):
	# 	cursor.execute(query)
	# 	results = cursor.fetchall()
	# 	if len(results) > 0:
	# 		return True
	# 	else:
	# 		return False

	def populateCancerTypeTable(self, inputFile, delimiter):
		cursor = self.db.cursor()
		cancerTypeInput = open(inputFile, "r")
		#read header
		header = cancerTypeInput.readline()
		header = header.strip().split(delimiter)
		isString = [1, 1]
		for line in cancerTypeInput:
			dataFields = line.strip().split(delimiter)
			valLine = self.processValues(dataFields, isString)
			sql = "INSERT INTO Cancer_Types(\
					cancer_type_id, %s, %s)\
					VALUES(%s)" %(header[0], header[1], valLine)

			try:
				cursor.execute(sql)
				self.db.commit()
			except:
				print "Error trying to input data %s, %s into cancer type table. Please check these values again." %(dataFields[0], dataFields[1])
				self.db.rollback()

	def populateGeneTable(self, inputFile, delimiter):
		cursor = self.db.cursor()
		geneTableInput = open(inputFile, "r")
		#read header line
		header = geneTableInput.readline()
		header = header.strip().split(delimiter)
		isString = [1, 1, 1, 0, 0, 1]
		for line in geneTableInput:
			dataFields = line.strip().split(delimiter)
			valLine = self.processValues(dataFields, isString)

			# existQuery = "SELECT *\
			# 			  FROM Genes\
			# 			  WHERE gene_name = '%s'" %(dataFields[0])
			# if(self.exists(cursor, existQuery)):
			# 	continue

			#form the sql query by parsing a line from the input file
			sql = "INSERT IGNORE INTO Genes(\
					gene_id, %s, %s, %s,\
					%s, %s, %s)\
					VALUES(%s)" %(header[0], header[1], header[2], header[3], header[4], header[5], valLine)

			try:
				cursor.execute(sql)
				self.db.commit()
			except:
				print "Error trying to input gene into table."
				print sql
				self.db.rollback()
				sys.exit()

	def populateExpPlatformTable(self, inputFile, delimiter):
		cursor = self.db.cursor()
		platformInput = open(inputFile, "r")

		#read header line
		header = platformInput.readline()
		header = header.strip().split(delimiter)
		isString = [1, 1]

		for line in platformInput:
			dataFields = line.strip().split(delimiter)
			valLine = self.processValues(dataFields, isString)

			#form the sql query by parsing a line from the input file
			sql = "INSERT INTO Exp_Platforms(\
					platform_id, %s, %s)\
					VALUES(%s)" %(header[0], header[1], valLine)

			try:
				cursor.execute(sql)
				self.db.commit()
			except:
				print "Error trying to input Exp_Platform into table."
				self.db.rollback()

	"""
	This function behaves differently than the other population functions. Since we generally
	have no input file for the Experiments table, this function just inputs single entries with
	the user providing the values for the respective data fields.

	@Parameters:
		model: String with the name of the model.
		description: String providing a description of the model.
		parameter_set: String listing out the parameters used for the model.
		name: String for the name of the experiment.
		exp_date: String of the date the experiment was done (format: "yyyy-mm-dd")
	"""
	def populateExperimentTable(self, model, description, parameter_set, name, exp_date):
		cursor = self.db.cursor()

		sqlInsert = "INSERT INTO Experiments\
					 VALUES(NULL, \"%s\", \"%s\", \"%s\", \"%s\", \"%s\")" %(model, description, parameter_set, name, exp_date)

		try:
			cursor.execute(sqlInsert)
			self.db.commit()
		except:
			print "Error trying to insert into 'Experiments' table. Please check arguments again."
			print sqlInsert
			self.db.rollback()

	def populateSGAUnitGroupTable(self, inputFile, delimiter):
		cursor = self.db.cursor()
		groupInput = open(inputFile, "r")

		#read header line
		header = groupInput.readline()
		header = header.strip().split(delimiter)
		header[1] = "cancer_type_id"
		isString = [1, 0, 1, 1]

		for line in groupInput:
			dataFields = line.strip().split(delimiter)

			#this database has a foreign key for the cancer_type_id, we need to find the corresponding ID given the cancer name
			sqlQuery = "SELECT cancer_type_id\
						FROM Cancer_Types\
						WHERE abbv = '%s'" %(dataFields[1])
			try:
				cursor.execute(sqlQuery)
				results = cursor.fetchall()
				if len(results) > 1:
					print "Found multiple rows with cancer name %s. Skipping." %(dataFields[1])
					continue
				#if corresponding ID was sucessfully found, replace the cancer_name in the input with the cancer_id
				dataFields[1] = results[0][0]
			except:
				print "Error: unable to fetch data."
				print sqlQuery
				continue

			#convert the values into proper SQL syntax
			valLine = self.processValues(dataFields, isString)

			#form the sql query
			sqlInsert = "INSERT INTO SGA_Unit_Group(\
						group_id, %s, %s, %s, %s)\
						VALUES(%s)" %(header[0], header[1], header[2], header[3], valLine)
			#print sqlInsert

			try:
				cursor.execute(sqlInsert)
				self.db.commit()
			except:
				print "Error trying to input SGA unit/group into table."
				self.db.rollback()	
				#sys.exit()

	def populatePatientTable(self, inputFile, delimiter):
		cursor = self.db.cursor()
		patientInput = open(inputFile, "r")

		#read header
		header = patientInput.readline()
		header = header.strip().split(delimiter)
		header[6] = "cancer_type_id" #cancer_name needs to be corresponding ID in our table (foreign key)
		isString = [1, 1, 1, 1, 1, 1, 0]

		for line in patientInput:
			dataFields = line.strip().split(delimiter)

			#this database has a foreign key for the cancer_type_id, we need to find the corresponding ID given the cancer name
			sqlQuery = "SELECT cancer_type_id\
						FROM Cancer_Types\
						WHERE abbv = '%s'" %(dataFields[6])
			try:
				cursor.execute(sqlQuery)
				results = cursor.fetchall()
				if len(results) > 1:
					print "Found multiple rows with cancer name %s. Skipping." %(dataFields[6])
					continue
				#if corresponding ID was sucessfully found, replace the cancer_name in the input with the cancer_id
				dataFields[6] = results[0][0]
			except:
				print "Error: unable to fetch data."
				print sqlQuery
				continue

			#convert the values into proper SQL syntax
			valLine = self.processValues(dataFields, isString)

			#form the sql query
			sqlInsert = "INSERT INTO Patients(\
						patient_id, %s, %s, %s, %s, %s, %s, %s)\
						VALUES(%s)" %(header[0], header[1], header[2], header[3], header[4], header[5], header[6], valLine)
			try:
				cursor.execute(sqlInsert)
				self.db.commit()
			except:
				print "Error trying to input patient into table."
				print sqlInsert
				self.db.rollback()	
				sys.exit()

	def populateSMTable(self, inputFile, delimiter):
		cursor = self.db.cursor()
		smInput = open(inputFile, "r")

		#read header
		header = smInput.readline()
		header = header.strip().split(delimiter)
		header[0] = "patient_id"
		header[1] = "gene_id"
		isString = [0, 0, 1, 1, 1, 0, 0, 2, 1, 1]

		for line in smInput:
			dataFields = line.strip().split(delimiter)

			#disregard SMs that have 'Unkown' as gene name
			if dataFields[1] == 'Unknown' or dataFields[1] == 'unknown':
				continue

			#query for patient id
			sqlQuery = "SELECT patient_id\
						FROM Patients\
						WHERE name = '%s'" %(dataFields[0])
			try:
				cursor.execute(sqlQuery)
				results = cursor.fetchall()
				if len(results) > 1:
					print "Retrieved more than one entry for patient %s. Skip." %(dataFields[0])
					continue
				dataFields[0] = results[0][0]
			except:
				print "Error: unable to fetch patient data."
				print sqlQuery
				#sys.exit()
				continue

			#query for gene id
			sqlQuery = "SELECT gene_id\
						FROM Genes\
						WHERE gene_name = '%s'" %(dataFields[1])
			try:
				cursor.execute(sqlQuery)
				results = cursor.fetchall()
				if len(results) > 1:
					print "Found more than one result for gene %s. Skip." %(dataFields[1])
					continue
				dataFields[1] = results[0][0]
			except:
				print "Error. Unable to fetch gene data."
				print sqlQuery
				#sys.exit()
				continue

			#process the rest of the line using 'processValues'
			valLine = self.processValues(dataFields, isString)
			
			sqlInsert = "INSERT INTO Somatic_Mutations(\
						sm_id, %s, %s, %s, %s, %s, %s, %s, aa_loc, aa_norm, aa_mut, %s, %s)\
						VALUES(%s)" %(header[0], header[1], header[2], header[3], header[4], header[5], header[6], header[8], header[9], valLine)
			try:
				cursor.execute(sqlInsert)
				self.db.commit()
			except:
				print "Error trying to insert SM."
				print sqlInsert
				self.db.rollback()
				sys.exit()  


	def populateSCNATable(self, inputFile, delimiter):
		cursor = self.db.cursor()
		scnaInput = open(inputFile, "r")

		#read header line
		header = scnaInput.readline()
		header = header.strip().split(delimiter)
		header[0] = "patient_id"
		header[1] = "gene_id"
		header[4] = "platform_id"
		isString = [0, 0, 1, 0, 0]

		for line in scnaInput:
			dataFields = line.strip().split(delimiter)

			#query for the foreign keys
			if dataFields[0] != "null" and dataFields[0] != "NULL":
				sqlQuery = "SELECT patient_id\
							FROM Patients\
							WHERE name = '%s'" %(dataFields[0])
				try:
					cursor.execute(sqlQuery)
					results = cursor.fetchall()
					if len(results) > 1:
						print "Retrieved more than one entry for patient %s. Skip." %(dataFields[0])
						continue
					dataFields[0] = results[0][0]
				except:
					print "Error: unable to fetch patient data."
					print sqlQuery
					#sys.exit()
					continue

			if dataFields[1] != "null" and dataFields[1] != "NULL":
				sqlQuery = "SELECT gene_id\
							FROM Genes\
							WHERE gene_name = '%s'" %(dataFields[1])
				try:
					cursor.execute(sqlQuery)
					results = cursor.fetchall()
					if len(results) > 1:
						print "Retrieved more than one entry for gene %s. Skip." %(dataFields[1])
						continue
					#print results
					dataFields[1] = results[0][0]
				except:
					print "Error: unable to fetch gene id."
					#print sqlQuery
					continue

			if dataFields[4] != "null" and dataFields[4] != "NULL":
				sqlQuery = "SELECT platform_id\
							FROM Exp_Platforms\
							WHERE platform = '%s'" %(dataFields[4])
				try:
					cursor.execute(sqlQuery)
					results = cursor.fetchall()
					if len(results) > 1:
						print "Retrieved more than one entry for platform %s. Skip." %(dataFields[4])
						continue
					dataFields[4] = results[0][0]
				except:
					print "Error: unable to fetch exp_platform_id."
					continue

			valLine = self.processValues(dataFields, isString)
			sqlInsert = "INSERT INTO SCNAs\
						(scna_id, %s, %s, %s, %s, %s)\
						VALUES(%s)" %(header[0], header[1], header[2], header[3], header[4], valLine)
			try:
				cursor.execute(sqlInsert)
				self.db.commit()
			except:
				print "Error trying to insert scna."
				print sqlInsert
				self.db.rollback()
				sys.exit()

	def populateDEGTable(self, inputFile, delimiter):
		cursor = self.db.cursor()
		degInput = open(inputFile, "r")

		#read header
		header = degInput.readline()
		header = header.strip().split(delimiter)
		header[0] = "patient_id"
		header[1] = "gene_id"
		header[3] = "platform_id"
		header.append("exp_id")
		isString = [0, 0, 1, 0, 1, 0]

		for line in degInput:
			dataFields = line.strip().split(delimiter)

			#query to find patient id
			patientQuery = "SELECT patient_id\
							FROM Patients\
							WHERE name = '%s'" %(dataFields[0])
			try:
				cursor.execute(patientQuery)
				results = cursor.fetchall()
				if len(results) > 1:
					print "Retrieved more than one entry for patient %s. Skip." %(dataFields[0])
					continue
				dataFields[0] = results[0][0]
			except:
				print "Error: unable to fetch patient_id."
				print patientQuery
				continue
				#sys.exit()

			#query to find gene_id
			geneQuery = "SELECT gene_id\
						FROM Genes\
						WHERE gene_name = '%s'" %(dataFields[1])
			try:
				cursor.execute(geneQuery)
				results = cursor.fetchall()
				if len(results) > 1:
					print "Retrieved more than one entry for gene %s. Skip." %(dataFields[1])
					continue
				dataFields[1] = results[0][0]
			except:
				print "Error: unable to fetch gene_id."
				print geneQuery
				continue
				#sys.exit()

			#query to find platform_id (given not null)
			if dataFields[3] != "null" and dataFields[3] != "Null":
				platformQuery = "SELECT platform_id\
								 FROM Exp_Platforms\
								 WHERE platform = '%s'" %(dataFields[3])
			 	try:
			 		cursor.execute(platformQuery)
			 		results = cursor.fetchall()
			 		if len(results) > 1:
			 			print "Retrieved more than one entry for platform %s. Skip." %(dataFields[3])
			 			continue
		 			dataFields[3] = results[0][0]
	 			except:
	 				print "Error: unable to fetch platform_id."
	 				print platformQuery
	 				continue
	 				#sys.exit()

			dataFields.append("2")
			valLine = self.processValues(dataFields, isString)

			sqlInsert = "INSERT INTO DEGs(\
						deg_id, %s, %s, %s, %s, %s, %s)\
						VALUES(%s)" %(header[0], header[1], header[2], header[3], header[4], header[5], valLine)
			try:
				cursor.execute(sqlInsert)
				self.db.commit()
			except:
				print "Error trying to insert DEG."
				print sqlInsert
				self.db.rollback()
				sys.exit()

	def populateTDIResults(self, inputFile, delimiter):
		cursor = self.db.cursor()
		tdiFile = open(inputFile, "r")

		header = tdiFile.readline()
		header = header.strip().split(delimiter)
		header[0] = "patient_id"
		header[1] = "gt_gene_id"
		header[2] = "ge_gene_id"
		header[4] = "exp_id"
		isString = [0, 0, 0, 0, 1]
		gene_or_group_flag = 0 #0 if gene, 1 if group

		for line in tdiFile:
			dataFields = line.strip().split(delimiter)

			#query for patient id
			patientQuery = "SELECT patient_id\
							FROM Patients\
							WHERE name = '%s'" %(dataFields[0])
			try:
				cursor.execute(patientQuery)
				results = cursor.fetchall()
				if len(results) > 1:
					print "Retrieved more than one entry for patient %s. Skip." %(dataFields[0])
					continue
				dataFields[0] = results[0][0]
			except:
				print "Error: unable to fetch patient_id."
				print patientQuery
				continue
				#sys.exit()

			#if 'SGA.unit' or 'SGA.group' in gene name, lookup the SGA_Unit_Group table instead
			if "group" not in dataFields[1] and "unit" not in dataFields[1]:
				gene_or_group_flag = 0

				#query for gt gene id
				gtQuery = "SELECT gene_id\
						   	FROM Genes\
						   	WHERE gene_name = '%s'" %(dataFields[1])
				try:
					cursor.execute(gtQuery)
					results = cursor.fetchall()
					if len(results) > 1:
						print "Retrieved more than one entry for GT %s. Skip." %(dataFields[1])
						continue
					dataFields[1] = results[0][0]
				except:
					print "Error: unable to fetch GT id."
					print gtQuery
					continue
					#sys.exit()
			else:
				gene_or_group_flag = 1

				gtQuery = "SELECT group_id\
						   FROM SGA_Unit_Group\
						   WHERE name = '%s'" %(dataFields[1])
				try:
					cursor.execute(gtQuery)
					results = cursor.fetchall()
					if len(results) > 1:
						print "Retrieved more than one entry for GT %s. Skip." %(dataFields[1])
						continue
					dataFields[1] = results[0][0]
				except:
					print "Error: unable to fetch group id."
					print gtQuery
					continue
					#sys.exit()

			#query for the ge gene id
			geQuery = "SELECT gene_id\
						FROM Genes\
						WHERE gene_name = '%s'" %(dataFields[2])
			try:
				cursor.execute(geQuery)
				results = cursor.fetchall()
				if len(results) > 1:
					print "Retrieved more than one entry for GE %s. Skip." %(dataFields[1])
					continue
				dataFields[2] = results[0][0]
			except:
				print "Error: unable to fetch GE id."
				print geQuery
				continue
				#sys.exit()

			#query for exp id (if not null)
			# if dataFields[4] != "null" and dataFields[4] != "Null":
			# 	expQuery = "SELECT exp_id\
			# 				FROM Experiments\
			# 				WHERE name = '%s'" %(dataFields[4])
			# 	try:
			# 		cursor.execute(expQuery)
			# 		results = cursor.fetchall()
			# 		if len(results) > 1:
			# 			print "Retrieved more than one entry for experiment %s. Skip." %(dataFields[4])
			# 			continue
			# 		dataFields[4] = results[0][0]
			# 	except:
			# 		print "Error: unable to fetch experiment id."
			# 		print expQuery
			# 		continue
			dataFields[4] = "2"

			valLine = self.processValues(dataFields, isString)


			#insert entry into TDI table
			if gene_or_group_flag == 0:
				sqlInsert = "INSERT INTO TDI_Results(\
							 tdi_id, %s, %s, %s, %s, %s)\
							 VALUES(%s)" %(header[0], "gt_gene_id", header[2], header[3], header[4], valLine)
			else:
				sqlInsert = "INSERT INTO TDI_Results(\
							 tdi_id, %s, %s, %s, %s, %s)\
							 VALUES(%s)" %(header[0], "gt_unit_group_id", header[2], header[3], header[4], valLine)
			try:
				cursor.execute(sqlInsert)
				self.db.commit()
			except:
				print "Error: unable to insert TDI entry."
				print sqlInsert
				self.db.rollback()
				sys.exit()


	##Given a TCGA gene name, return the corresponding geneID from the 'Genes' table
	#@param geneName TCGA gene name
	#@return geneID id of gene in TDI database	
	def getGeneID(self, geneName):
		cursor = self.db.cursor()
		query = "SELECT gene_id\
				 FROM Genes\
				 WHERE gene_name = '%s'" %(geneName)
		try:
			cursor.execute(query)
			results = cursor.fetchall()
			return int(results[0][0])
		except:
			print "Error finding gene id. Please ensure that given gene %s is a proper gene name. Otherwise %s is not in the database." %(geneName, geneName)
			return "null"


	## 	Get the experiment ID from the Experiments table given a versionID
	#	@param versionName versionID of the TCGA data
	#	@return experimentID experiment ID of the corresponding data version
	def getExpID(self, versionName):
		cursor = self.db.cursor()
		expQuery = "SELECT exp_id\
					FROM Experiments\
					WHERE name = 'v%s'" %(versionName)
		cursor.execute(expQuery)
		return cursor.fetchall()[0][0]

	
	##	Get the view name given the versionID and the mutation type ('SM' or 'SCNA')
	#	@param versionName versionID of the TCGA data
	#	@param mut_type 'SM' or 'SCNA' for Somatic Mutation or Copy number alteration data respectively
	#	@return viewName the name of the appropriate view given versionID and mut_type
	def getView(self, versionName, mut_type):
		cursor = self.db.cursor()
		query = "SELECT view_name\
				 FROM Version_To_View\
				 WHERE version_name = '%s' AND mut_type = '%s'" %(versionName, mut_type)
		try:
			cursor.execute(query)
			results = cursor.fetchall()
			return str(results[0][0])
		except:
			print "Error finding view. Please ensure that the given version exists in our database."
			return


	##	Gets the most frequently called driver genes and their frequencies given a version of the TCGA data and a number for the top 'x' drivers,
	#	@param versionName version of the TCGA data (e.g. 9, 9.5 etc)
	#	@param numDrivers number of drivers to return (if '50', function will return top 50 drivers ordered by frequency)
	#	@return List of tuples containing the driver genes and their frequencies  
	def getTopDrivers(self, versionName, numDrivers):
		cursor = self.db.cursor()
		expID = self.getExpID(versionName)

		topDriversQuery = "SELECT gene_name, COUNT(DISTINCT(patient_id)) AS num_tumors\
						   FROM TDI_Results JOIN Genes ON TDI_Results.gt_gene_id = Genes.gene_id\
						   WHERE exp_id = %s AND gene_name != 'A0'\
						   GROUP BY gt_gene_id\
						   ORDER BY num_tumors DESC LIMIT %d" %(expID, numDrivers)
	   	cursor.execute(topDriversQuery)
	   	results = cursor.fetchall()
	   	return results

   	##	Gets the number of tumors in the TDI database with the given gene as a driver.
   	#	@param gtGene valid TCGA gene name for the driver gene
   	#	@param versionName version of the TDI data of interest
   	#	@return numTumors number of tumors in TDI with 'gtGene' as a driver for a given version of TDI
   	def countTDITumors(self, gtGene, versionName):
   		cursor = self.db.cursor()

   		geneID = self.getGeneID(gtGene)
   		expID = self.getExpID(versionName)

   		numTumorsQuery = "SELECT COUNT(DISTINCT(patient_id))\
   						  FROM TDI_Results\
   						  WHERE gt_gene_id = %s AND exp_id = %s" %(geneID, expID)

	  	cursor.execute(numTumorsQuery)
	  	results = cursor.fetchall()
	  	return int(results[0][0])


	##	Get number of tumors with a mutation of a TCGA gene
	#	@param geneName TCGA gene name of the gene of interest
	#	@return numTumors number of tumors in our database with mutation of 'geneName'
	def getNumTumorsWithMutation(self, geneName):
		cursor = self.db.cursor()
		geneID = self.getGeneID(geneName)

		query = "SELECT COUNT(DISTINCT(patient_id))\
				 FROM Somatic_Mutations\
				 WHERE gene_id = %s AND mut_type != 'synonymous SNV'" %(geneID)

		cursor.execute(query)
		results = cursor.fetchall()
		return int(results[0][0])

	##	Get number of tumors with deletion of 'geneName'
	#	@param geneName TCGA gene name of the gene of interest
	#	@param versionID version ID for TCGA dataset
	#	@return numTumors number of tumors with deletion of 'geneName'
	def getNumTumorsWithDeletion(self, geneName, versionID):
		cursor = self.db.cursor()
		geneID = self.getGeneID(geneName)
		view = self.getView(versionID, "SCNA")

		query = "SELECT COUNT(DISTINCT(patient_id))\
    			 FROM %s\
    			 WHERE gt_gene_id = %s AND gistic_score = -2" %(view, geneID)

		cursor.execute(query)
		results = cursor.fetchall()
		return int(results[0][0])


	##	Find all tumors (patients) with a given driver gene.
	#	@param gtGene: TCGA gene name
	#	@param mutType: optional parameter to condition the query only on tumors with synonymous or nonsynonymous mutations of gtGene
	#	@return list of patient IDs
	def findTumorsWithGT(self, gtGene, mutType = 'all'):
		cursor = self.db.cursor()

		if mutType != 'all' and mutType != 'syn' and mutType != 'nonsyn':
			print "Error with type argument, proceeding to find all tumors. Please ensure that the given 'mutType' argument\
					is either 'all', 'syn', or 'nonsyn'."
			mutType = 'all'

		if mutType == 'all':
			query = "SELECT DISTINCT patient_id\
					FROM TDI_Results JOIN Genes ON TDI_Results.gt_gene_id = Genes.gene_id\
					WHERE Genes.gene_name = '%s' AND TDI_Results.gt_gene_id IS NOT NULL" %(gtGene)

		elif mutType == 'syn':
			query = "SELECT DISTINCT patient_id\
					FROM TDI_Results JOIN Genes ON TDI_Results.gt_gene_id = Genes.gene_id\
				    JOIN Somatic_Mutations ON Somatic_Mutations.patient_id = Patients.patient_id AND Somatic_Mutations.gene_id = Genes.gene_id\
					WHERE Genes.gene_name = '%s' AND TDI_Results.gt_gene_id IS NOT NULL AND Somatic_Mutations.mut_type = 'synonymous SNV'" %(gtGene)

		elif mutType == 'nonsyn':
			query = "SELECT DISTINCT patient_id\
					FROM TDI_Results JOIN Genes ON TDI_Results.gt_gene_id = Genes.gene_id\
				    JOIN Somatic_Mutations ON Somatic_Mutations.patient_id = Patients.patient_id AND Somatic_Mutations.gene_id = Genes.gene_id\
					WHERE Genes.gene_name = '%s' AND TDI_Results.gt_gene_id IS NOT NULL AND Somatic_Mutations.mut_type = 'nonsynonymous SNV'" %(gtGene)


		try:
			cursor.execute(query)
			results = cursor.fetchall()
			return [r[0] for r in results]
		except:
			print "Error. Unable to process query."
			print query 
			return

	##	Get the number of tumors with a mutation of a given gene at a given location
	#	@param gtGene TCGA gene name for gene of interest
	#	@param aaLoc Amino acid location of interest
	#	@return numTumors number of tumors with mutation of gtGene at aaLoc
	def numberOfTumorsWithGTAtLocation(self, gtGene, aaLoc):
		cursor = self.db.cursor()

		geneID = self.getGeneID(gtGene)

		query = "SELECT COUNT(DISTINCT(patient_id))\
				 FROM TDI_SM\
				 WHERE gt_gene_id = %s AND aa_loc = %s" %(geneID, aaLoc)
		try:
			cursor.execute(query)
			results = cursor.fetchall()
			return int(results[0][0])
		except:
			print "Error executing query."
			print query
			return


	##	Get all tumors with a mutation for 'gtGene' at location 'aaLoc'
	#	@param gtGene TCGA gene name for gene of interest
	#	@param aaLoc Amino acid position of interest
	#	@param versionID version ID of the TCGA dataset of interest (9, 9.5 etc.)
	#	@return tumorList List of tumors with mutation in 'gtGene' at 'aaLoc'
	def getTumorsMutatedWithGTAtLocation(self, gtGene, versionID, aaLoc):
		cursor = self.db.cursor()

		geneID = self.getGeneID(gtGene)
		view = self.getView(versionID, "SM")

		query = "SELECT DISTINCT(patient_id)\
				 FROM %s\
				 WHERE gt_gene_id = %s AND aa_loc = %s" %(view, geneID, aaLoc)
		try:
			cursor.execute(query)
			results = cursor.fetchall()
			return [x[0] for x in results]
		except:
			print "Error executing query to get tumors at a given location."
			print query
			return	

	## Get all DEGs for a given SGA (gtGene) and TDI versionID
	#	@param TCGA gene name for gene of interest
	#	@param versionID version ID of the TCGA dataset of interest (e.g. 9, 9.5)
	#	@param threshold minimum percentage of tumors with a GT-GE relationship needed to count the GE as a target for the GT
	#	@return degList List of DEGs found by the given version of TDI for the given SGA
	def getDEGsForSGA(self, gtGene, versionID, threshold = 0.2):
		cursor = self.db.cursor()
		geneID = self.getGeneID(gtGene)
		expID = self.getExpID(versionID)
		totalNumTumors = self.countTDITumors(gtGene, versionID)

		degQuery = "SELECT gene_name, COUNT(DISTINCT(patient_id)) AS num_tumors\
					FROM TDI_Results JOIN Genes ON TDI_Results.ge_gene_id = Genes.gene_id\
					WHERE gt_gene_id = %s AND exp_id = %s\
					GROUP BY gene_name\
					HAVING num_tumors / %s >= %s" %(geneID, expID, totalNumTumors, threshold)

		try:
			cursor.execute(degQuery)
			results = cursor.fetchall()
			return results
		except:
			print "Error getting DEGs for given SGA."
			print degQuery
			quit()

	##	Retrieves DEGs for a given SGA gene at a given amino acid location.
	#	@param geneName a TCGA geneID
   	#	@param hsLocation an int representation of a nucleosome location of interest
   	#	@param versionID version of TCGA data
	#	@return hotspotDict hotspotDict[ge] = # of tumors with ge affected by given gt
	def findDEGsAtHotspot(self, geneName, hsLocation, versionID, minTumors=0):
		cursor = self.db.cursor()
		#first find geneID of the given gene name
		geneID = self.getGeneID(geneName)
		view = self.getView(versionID, "SM")

		#find all degs
		hotspotQuery = "SELECT gene_name, COUNT(DISTINCT(patient_id)) AS num_tumors\
						FROM %s JOIN Genes ON Genes.gene_id = %s.ge_gene_id\
						WHERE aa_loc = %s AND gt_gene_id = %s\
						GROUP BY ge_gene_id\
						HAVING num_tumors > %s\
						ORDER BY num_tumors DESC" %(view, view, hsLocation, geneID, minTumors)
		try:
			cursor.execute(hotspotQuery)
			results = cursor.fetchall()
			return results
			# hsDict = {}
			# for tup in results:
			# 	hsDict[tup[0]] = int(tup[1])
			# return hsDict
		except:
			print "Error. Unable to process query."
			print hotspotQuery
			return


	##	Find all DEGs regulated by a GT gene for a given patient
	#	@param gtGene TCGA gene name for driver gene of interest
	#	@param patientID patient id (in our database) for the patient of interest
	#	@return degList list of DEGs regulated by 'gtGene' for 'patientID'
	def getDEGsForPatientAndGT(self, gtGene, patientID):
		cursor = self.db.cursor()
		geneID = self.getGeneID(gtGene)

		degQuery = "SELECT DISTINCT(gene_name)\
					FROM TDI_Results JOIN Genes ON TDI_Results.ge_gene_id = Genes.gene_id\
					WHERE gt_gene_id = %s AND patient_id = %s" %(geneID, patientID)
		try:
			cursor.execute(degQuery)
			results = cursor.fetchall()
			return [x[0] for x in results]
		except:
			print "Error retrieving DEGs for GT: %s and patientID: %s." %(gtGene, patientID)
			return "null"


	##	Find top hotspot mutation locations for a given gene
	#	@param geneName TCGA gene name for gene of interest
	#	@param versionName version ID for the TCGA data of interest
	#	@param numHotspots number of hotspots to be returned (will find top 'x' hotspots)
	#	@return hsList List of amino acid locations representing the hotspots for the given gene
	def findTopHotspots(self, geneName, versionName, numHotspots):
		cursor = self.db.cursor()
		geneID = self.getGeneID(geneName)
		view = self.getView(versionName, "SM")

		#find top hotspots for gene
		hotspotQuery = "SELECT aa_loc, COUNT(DISTINCT(patient_id)) AS num_tumors\
						FROM %s\
						WHERE gt_gene_id = %s\
						GROUP BY aa_loc\
						ORDER BY num_tumors DESC LIMIT %s" %(view, geneID, numHotspots)
		try:
			cursor.execute(hotspotQuery)
			results = cursor.fetchall()
			hsList = [[int(tup[0]), int(tup[1])] for tup in results]
			return hsList
		except:
			print "Error retrieving hotspots. Make sure gene name is an official TCGA gene."
			print hotspotQuery
			return 

	##	Find the DEGs associated with mutation of a given gtGene at the top hotspot locations
	#	@param geneName TCGA gene name for gene of interest
	#	@param numHotspots number of hotspots to be examined (will find top 'x' hotspots)
	#	@param version Version of the TDI data to query (e.g. 9, 9.5 etc.)
	#	@return hsDict dictionary with the keys being the hotspot location, value being a list of tuples containing the DEG and number of tumors in which it occurs
	def findTopHotspotsWithDEGs(self, geneName, numHotspots, version):
		hsList = self.findTopHotspots(geneName, numHotspots)
		cursor = self.db.cursor()
		hsDict = {}

		view = self.getView(version, "SM")

		# viewQuery = "SELECT view_name\
		# 			 FROM Version_To_View\
		# 			 WHERE version_name = '%s'" %(version)
		# try:
		# 	cursor.execute(viewQuery)
		# 	results = cursor.fetchall()
		# 	view = str(results[0][0])
		# except:
		# 	print "Error retrieving view with the given version name."
		# 	return

		for hs in hsList:
			geQuery = "SELECT gene_name, COUNT(DISTINCT(patient_id)) AS num_tumors\
						FROM %s JOIN Genes ON Genes.gene_id = TDI_SM.ge_gene_id\
						WHERE aa_loc = %s AND gt_gene_id = %s\
						GROUP BY ge_gene_id" %(view, hs[0], geneID)
			try:
				cursor.execute(geQuery)
				results = cursor.fetchall()
				hsDict[hs[0]] = []
				for tup in results:
					hsDict[hs[0]].append((tup[0], int(tup[1])))
				hsDict[hs[0]] = sorted(hsDict[hs[0]], key=lambda x: x[1], reverse = True)
			except:
				print "Error retrieving degs for hotspot. Skipping."
				print geQuery
				continue

		return hsDict

	##	Given two distinct TCGA driver gene IDs, find overlapping DEG targets between the two drivers from our algorithm.
	#	@param gene1 TCGA gene ID for driver gene 1
	#	@param gene2 TCGA gene ID for driver gene 2
	#	@return commonTargets list of DEGs that have cases of being driven by gene1 or gene2 
	def findOverlappingTargets(self, gene1, gene2):
		cursor = self.db.cursor()

		#get gene IDs from given gene names
		gene1Query = "SELECT gene_id\
					  FROM Genes\
					  WHERE gene_name = '%s'" %(gene1)
		try:
			cursor.execute(gene1Query)
			geneID1 = int(cursor.fetchall()[0][0])
		except:
			print "Error retrieving gene ID for gene: %s." %(gene1)
			return

		gene2Query = "SELECT gene_id\
					  FROM Genes\
					  WHERE gene_name = '%s'" %(gene2)
		try:
			cursor.execute(gene2Query)
			geneID2 = int(cursor.fetchall()[0][0])
		except:
			print "Error retrieving gene ID for gene: %s." %(gene2)
			return

		#get degList and frequencies for gene1
		degQuery1 = "SELECT gene_name, COUNT(DISTINCT(patient_id)) AS num_tumors\
					 FROM TDI_Results JOIN Genes ON TDI_Results.ge_gene_id = Genes.gene_id\
					 WHERE gt_gene_id = %s\
					 GROUP BY ge_gene_id\
					 HAVING COUNT(DISTINCT(patient_id)) > 5\
					 ORDER BY num_tumors DESC" %(geneID1)
		try:
			cursor.execute(degQuery1)
			degsForGene1 = cursor.fetchall()
		except:
			print "Error finding targets for gene %s" %(gene1)
			print geneID1
			return

		#get degList and frequencies for gene2
		degQuery2 = "SELECT gene_name, COUNT(DISTINCT(patient_id)) AS num_tumors\
					 FROM TDI_Results JOIN Genes ON TDI_Results.ge_gene_id = Genes.gene_id\
					 WHERE gt_gene_id = %s\
					 GROUP BY ge_gene_id\
					 HAVING COUNT(DISTINCT(patient_id)) > 5\
					 ORDER BY num_tumors DESC" %(geneID2)
		try:
			cursor.execute(degQuery2)
			degsForGene2 = cursor.fetchall()
		except:
			print "Error finding targets for gene %s" %(gene2)
			return

		#find intersecting DEG targets between gene1 and gene2
		geneList1 = set([x[0] for x in degsForGene1])
		geneList2 = set([x[0] for x in degsForGene2])
		commonTargets = geneList1.intersection(geneList2)
		return commonTargets

	##	Given a TCGA gene ID for a target gene, find all driver genes that
	#	drive the target gene in at least a given number of tumors.
	#	@param targetGene TCGA gene ID for a target gene of interest
	#	@param minNumberOfTumors (optional) the minimum number of tumors for which we see a particular
	#			driver-target interaction in order for the algorithm to deem it significant
 	#	@return Results table detailing the driver genes found by the algorithm as well as the number of tumors with the given driver-target interaction
	def findDriversForGene(self, targetGene, minNumberOfTumors = 0):
		cursor = self.db.cursor()

		targetGeneID = self.getGeneID(targetGene)
		if targetGeneID != "null":
			driverGeneAndFreqQuery = "SELECT gene_name, COUNT(DISTINCT(patient_id)) AS num_tumors\
									  FROM TDI_Results JOIN Genes ON TDI_Results.gt_gene_id = Genes.gene_id\
									  WHERE ge_gene_id = %s\
									  GROUP BY gt_gene_id\
									  HAVING num_tumors > %s\
									  ORDER BY num_tumors DESC" %(targetGeneID, minNumberOfTumors)

			try:
				cursor.execute(driverGeneAndFreqQuery)
				results = cursor.fetchall()
				return results
			except:
				print "Could not execute query to find driver genes. Please ensure gene: %s is a standard TCGA gene name." %(targetGene)
				return
		else:
			return "null"

	##	Given a Python list of genes, this function looks at our Somatic_Mutation
	#	table and finds the tumors without a mutation in any of the given genes.
	#	This list of genes is returned to the user.
	#	@param geneList a Python list of TCGA gene IDs of genes to check for the absence of mutation
	#	@return A list of TCGA tumors found to not have mutations in any of the given genes in geneList
	def findTumorsWithoutGenes(self, geneList):
		cursor = self.db.cursor()
		geneString = ""
		for i in range(len(geneList)):
			if i == 0:
				geneString += "'" + geneList[i] + "'"
			else:
				geneString += ",'" + geneList[i] + "'"

		tumorQuery = "SELECT DISTINCT(name)\
		 			  FROM Somatic_Mutations JOIN Patients ON Somatic_Mutations.patient_id = Patients.patient_id\
					  WHERE Somatic_Mutations.patient_id NOT IN (SELECT DISTINCT(patient_id) FROM Somatic_Mutations JOIN Genes ON Somatic_Mutations.gene_id = Genes.gene_id WHERE gene_name IN (%s))" %(geneString)

	  	try:
	  		cursor.execute(tumorQuery)
	  		results = cursor.fetchall()
	  		return [x[0] for x in results]
	  		# return results
  		except:
  			print "Error with query."
  			return

	##	Given a TCGA driver gene and an integer value 'x' for the top x hotspots,
	#	this function first finds the top x hotspots based on somatic mutation frequency,
	#	then for each hotspot, it finds the tumors with mutations of the gene at the hotspot.
	#	Finally, for each of these tumors, we find the DEGs deemed to be driven by the gtGene
	#	in the tumor. These DEGs and their frequency of occurrence are ultimately returned to
	#	the user.
	#
	#	@param gtGene TCGA gene ID of driver gene of interest
	#	@param numHotspots Integer representing the top 'x' hotspots for the algorithm to look at
	#	@param versionID version ID for the TCGA dataset of interest
	#	@return degDict dictionary where keys are DEGs and value is the number of tumors (with mutation at a hotspot) have this DEG.
	#	@return len(deletionTumors) total number of tumors found with nonsynonymous mutation at one of the 'x' hotspots
	def findDEGsForTumorsAtTopHotspots(self, gtGene, numHotspots, versionID, minTumors=0):
		cursor = self.db.cursor()

		geneID = self.getGeneID(gtGene)

		#find top 5 hotspots in regards to nonsynonymous
		hotspotQuery = "SELECT aa_loc\
						FROM Somatic_Mutations\
						WHERE gene_id = %s AND mut_type = 'nonsynonymous SNV'\
						GROUP BY aa_loc\
						ORDER BY COUNT(DISTINCT(patient_id)) DESC LIMIT %s" %(geneID, numHotspots)
		try:
			cursor.execute(hotspotQuery)
			topHotspots = cursor.fetchall()
			topHotspots = [int(x[0]) for x in topHotspots]
		except:
			print "Error finding hotspots for %s." %(gtGene)
			return

		mutatedTumors = set()
		for hotspot in topHotspots:
			#find tumors for each hotspot
			tumorResults = self.getTumorsMutatedWithGTAtLocation(gtGene, versionID, hotspot)
			for tumor in tumorResults:
				mutatedTumors.add(tumor)

		degDict = {}
		for tumor in mutatedTumors:
			# degQuery = "SELECT DISTINCT(gene_name)\
			# 			FROM TDI_Results JOIN Genes ON TDI_Results.ge_gene_id = Genes.gene_id\
			# 			WHERE gt_gene_id = %s AND patient_id = %s" %(geneID, tumor)
			# try:
			# 	cursor.execute(degQuery)
			# 	degList = cursor.fetchall()
			# except:
			# 	print "Problem getting DEGs for patient ID: %s" %(tumor)
			# 	continue
			degList = self.getDEGsForPatientAndGT(gtGene, tumor)
			for deg in degList:
				if deg not in degDict:
					degDict[deg] = 1
				else:
					degDict[deg] += 1

		keysToRemove = []

		for k in degDict:
			if degDict[k] < minTumors:
				keysToRemove.append(k)

		for k in keysToRemove:
			degDict.pop(k, None)

		return degDict, len(mutatedTumors)

	##	Given a TCGA gene, this function finds the patients (tumors) in the
	#	SCNA table that have a deletion of the gene, then, for each patient,
	#	gets the DEGs found to be regulated by the deletion.
	#
	#	@param gtGene TCGA gene ID
	#	@param versionID version ID for TCGA data
	#	@return degDict dictionary where keys are DEGs and value is the number of tumors (with deletion of gtGene) have this DEG.
	#	@return len(deletionTumors) total number of tumors found with deletion of gtGene in SCNA table
	def findDEGsWithDeletion(self, gtGene, versionID, minTumors=0):
		cursor = self.db.cursor()

		view = self.getView(versionID, "SCNA")
		geneID = self.getGeneID(gtGene)
		deletionTumorsQuery = "SELECT DISTINCT(patient_id)\
							   FROM %s\
							   WHERE gt_gene_id = %s AND gistic_score = -2" %(view, geneID)
		try:
			cursor.execute(deletionTumorsQuery)
			deletionTumors = cursor.fetchall()
			deletionTumors = [x[0] for x in deletionTumors]
		except:
			print "Error retrieving tumors with deletion for gene %s." %(gtGene)
			print deletionTumorsQuery
			return

		#degSet = set()
		degDict = {}
		for tumor in deletionTumors:
			degList = self.getDEGsForPatientAndGT(gtGene, tumor)
			for deg in degList:
				if deg not in degDict:
					degDict[deg] = 1
				else:
					degDict[deg] += 1

		keysToRemove = []
		for k in degDict:
			if degDict[k] < minTumors:
				keysToRemove.append(k)

		for k in keysToRemove:
			degDict.pop(k, None)

		return degDict, len(deletionTumors)

	##	Get any GTs that are found to simultaneously regulate a pair of given GE genes.
	#	@param ge1 TCGA gene name for first GE
	#	@param ge2 TCGA gene name for second GE
	#	@return resultsDict dictionary in which keys are GT genes and the corresponding values are the number of patients in which this relationship occurs
	def findCommonGTs(self, ge1, ge2, versionName):
		cursor = self.db.cursor()

		ge1ID = self.getGeneID(ge1)
		ge2ID = self.getGeneID(ge2)
		expID = self.getExpID(versionName)

		ge1Dict = {}
		ge2Dict = {}

		ge1Query = "SELECT patient_id, gene_name\
					FROM TDI_Results JOIN Genes ON TDI_Results.gt_gene_id = Genes.gene_id\
					WHERE ge_gene_id = %s AND exp_id = %s" %(ge1ID, expID)

		cursor.execute(ge1Query)
		results = cursor.fetchall()
		for tup in results:
			ge1Dict[int(tup[0])] = tup[1]

		ge2Query = "SELECT patient_id, gene_name\
					FROM TDI_Results JOIN Genes ON TDI_Results.gt_gene_id = Genes.gene_id\
					WHERE ge_gene_id = %s AND exp_id = %s" %(ge2ID, expID)

		cursor.execute(ge2Query)
		results = cursor.fetchall()
		for tup in results:
			ge2Dict[int(tup[0])] = tup[1]

		commonPatients = set(ge1Dict.keys()).intersection(set(ge2Dict.keys()))

		resultsDict = {}

		for patient in commonPatients:
			if ge1Dict[patient] == ge2Dict[patient]:
				if ge1Dict[patient] in resultsDict:
					resultsDict[ge1Dict[patient]] += 1
				else:
					resultsDict[ge1Dict[patient]] = 1

		return resultsDict

	##	Closes connection to the database.
	def closeDB(self):
		self.db.close()

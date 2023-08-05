A lot of functions for bioinfomatics.

For example
	Ddict    Mulitiple dimension Hash
	Fastq_check	 Fastq Read
	Block_Reading A function for block Reading
	
Ddict Example
	from lpp import Ddict
	new_hash = Ddict()
	new_hash[3][4]=""
	new_hash[4][8] = ""
	for key in new_hash:
		for key2 in new_has[key]:
			print(  key1,key2 )
			
			
Fastq_check Example	

	from lpp import Fastq_check
	DATA= Fastq_check( open("read1.fastq",'rU')    )
	for a,b,c,b in DATA:
	
		print(a,b,c,d)
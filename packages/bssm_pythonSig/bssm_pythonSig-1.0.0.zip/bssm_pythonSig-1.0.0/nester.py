bssm = [["태혁햄","동민햄","지빈","태성"],"핵정한"]
def back(bssm):
	for pythonSig in bssm:
		if isinstance(pythonSig,list):
			back(pythonSig)
		else:
			print(pythonSig)

				


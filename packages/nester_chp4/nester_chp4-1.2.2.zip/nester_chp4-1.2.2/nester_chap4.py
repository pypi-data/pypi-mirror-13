"""포함된 리스트가 있을 경우, 그것을 포함해서 리스트의 모든 항목을 화면에 출력"""
def print_lol(the_list, indent=False, level=0, fh=sys.stdout):
		"""리스트를 받아 매 라인마다 리스트 항목에 이이 하나씩 재귀적으로출력"""
    for each_item in the_list:
		if isinstance(each_item, list):
			print_lol(each_item, indent, level+1, fh)
		else:
			if indent:	
				for tab_stop in range(level):
					print("\t", end='', file=fh)        
            print(each_item, file=fh)
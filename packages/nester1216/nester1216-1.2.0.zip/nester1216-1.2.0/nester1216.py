"""포함된 리스트가 있을 경우, 그것을 포함해서 리스트의 모든 항목을 화면에 출력"""
def print_lol(the_list, level=0):
		"""리스트를 받아 매 라인마다 리스트 항목에 이이 하나씩 재귀적으로출력"""
    for each_item in the_list:
	if isinstance(each_item, list):
	    print_lol(each_item, level+1)
	else:
            for tab_stop in range(level):
                print("\t", end='')        
            print(each_item)

						

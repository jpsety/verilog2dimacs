import re

def verilog2dimacs(path):

	regex = "(or|nor|and|nand|not|xor|xnor)\s+\S+\s*\((.+?)\);"
	top = path.split('/')[-1].replace('.v','')

	with open(path, 'r') as f:
		data = f.read()

	net_map = {}
	clauses = []

	for gate, net_str in re.findall(regex,data,re.DOTALL):

		# parse all nets
		nets = net_str.replace(" ","").replace("\n","").replace("\t","").split(",")
		out = nets[0]

		for net in nets:
			if net not in net_map:
				net_map[net] = len(net_map)+1

		if gate == 'and':
			exp = f'{net_map[out]}'
			for inp in nets[1:]:
				clauses.append(f'-{net_map[out]} {net_map[inp]} 0')
				exp += f' -{net_map[inp]}'
			exp += ' 0'
			clauses.append(exp)

		elif gate == 'nand':
			exp = f'-{net_map[out]}'
			for inp in nets[1:]:
				clauses.append(f'{net_map[out]} {net_map[inp]} 0')
				exp += f' -{net_map[inp]}'
			exp += ' 0'
			clauses.append(exp)

		elif gate == 'or':
			exp = f'-{net_map[out]}'
			for inp in nets[1:]:
				clauses.append(f'{net_map[out]} -{net_map[inp]} 0')
				exp += f' {net_map[inp]}'
			exp += ' 0'
			clauses.append(exp)

		elif gate == 'nor':
			exp = f'{net_map[out]}'
			for inp in nets[1:]:
				clauses.append(f'-{net_map[out]} -{net_map[inp]} 0')
				exp += f' {net_map[inp]}'
			exp += ' 0'
			clauses.append(exp)

		elif gate == 'not':
			clauses.append(f'{net_map[out]} {net_map[nets[1]]} 0')
			clauses.append(f'-{net_map[out]} -{net_map[nets[1]]} 0')

		elif gate == 'xor':
			while len(nets)>3:
				#create new net
				new_net = nets[-2]+nets[-1]
				net_map[new_net] = len(net_map)+1

				# add constraints
				clauses.append(f'-{net_map[new_net]} -{net_map[nets[-1]]} -{net_map[nets[-2]]} 0')
				clauses.append(f'-{net_map[new_net]} {net_map[nets[-1]]} {net_map[nets[-2]]} 0')
				clauses.append(f'{net_map[new_net]} -{net_map[nets[-1]]} {net_map[nets[-2]]} 0')
				clauses.append(f'{net_map[new_net]} {net_map[nets[-1]]} -{net_map[nets[-2]]} 0')

				# remove last 2 nets
				nets = nets[:-2]

				# insert before out
				nets.insert(1,new_net)

			# add constraints
			clauses.append(f'-{net_map[out]} -{net_map[nets[-1]]} -{net_map[nets[-2]]} 0')
			clauses.append(f'-{net_map[out]} {net_map[nets[-1]]} {net_map[nets[-2]]} 0')
			clauses.append(f'{net_map[out]} -{net_map[nets[-1]]} {net_map[nets[-2]]} 0')
			clauses.append(f'{net_map[out]} {net_map[nets[-1]]} -{net_map[nets[-2]]} 0')

		elif gate == 'xnor':
			while len(nets)>3:
				#create new net
				new_net = nets[-2]+nets[-1]
				net_map[new_net] = len(net_map)+1

				# add constraints
				clauses.append(f'-{net_map[new_net]} -{net_map[nets[-1]]} -{net_map[nets[-2]]} 0')
				clauses.append(f'-{net_map[new_net]} {net_map[nets[-1]]} {net_map[nets[-2]]} 0')
				clauses.append(f'{net_map[new_net]} -{net_map[nets[-1]]} {net_map[nets[-2]]} 0')
				clauses.append(f'{net_map[new_net]} {net_map[nets[-1]]} -{net_map[nets[-2]]} 0')

				# remove last 2 nets
				nets = nets[:-2]

				# insert before out
				nets.insert(1,new_net)

			#create new net
			new_net = out+'_xnor'
			net_map[new_net] = len(net_map)+1

			# add constraints
			clauses.append(f'-{net_map[new_net]} -{net_map[nets[-1]]} -{net_map[nets[-2]]} 0')
			clauses.append(f'-{net_map[new_net]} {net_map[nets[-1]]} {net_map[nets[-2]]} 0')
			clauses.append(f'{net_map[new_net]} -{net_map[nets[-1]]} {net_map[nets[-2]]} 0')
			clauses.append(f'{net_map[new_net]} {net_map[nets[-1]]} -{net_map[nets[-2]]} 0')
			clauses.append(f'{net_map[out]} {net_map[new_net]} 0')
			clauses.append(f'-{net_map[out]} -{net_map[new_net]} 0')
	# handle assigns
	assign_regex = "assign\s+(\S+)\s*=\s*(\S+);"
	for n0, n1 in re.findall(assign_regex,data):

		# ensure that the net is in the map
		for net in (n0,n1):
			if net not in net_map:
				net_map[net] = len(net_map)+1

		# tie nets together
		clauses.append(f'-{net_map[n0]} {net_map[n1]} 0')
		clauses.append(f'{net_map[n0]} -{net_map[n1]} 0')

	# constrain 1'b1 and 1'b0 nets
	if '1\'b0' in net_map:
		clauses.append(f"-{net_map['1\'b0']} 0")
	if '1\'b1' in net_map:
		clauses.append(f"{net_map['1\'b1']} 0")

	return top,net_map,clauses


def constrain(constraints,net_map,clauses):
	new_clauses = clauses.copy()
	for net,value in constraints.items():
		literal = net_map[net] if value else -net_map[net]
		new_clauses.append(f'{literal} 0')
	return new_clauses


def write(top,net_map,clauses):
	with open(f'{top}.dimacs','w') as f:
		f.write(f'c {top}\np cnf {len(net_map)} {len(clauses)}\n'+'\n'.join(clauses)+'\n')
	with open(f'{top}.map','w') as f:
		f.write(str(net_map))

if __name__ == '__main__':
	import sys
	from itertools import product
	import subprocess

	top,net_map,clauses = verilog2dimacs(sys.argv[1])
	print(f'top: {top}')
	print(f'net_map: {net_map}')
	print(f'clauses: {clauses}')

	constraints = {list(net_map.keys())[-1]:1}
	cons_clauses = constrain(constraints,net_map,clauses)
	print(f'cons_clauses: {cons_clauses}')

	write(top,net_map,clauses)

	# get inputs and nets
	with open(sys.argv[1],'r') as f:
		data = f.read()

	inps = []
	for m in re.findall('input (.+?);',data):
		inps += m.replace(' ','').split(',')
	print(inps)

	nets = set()
	for _,m in re.findall('(or|nor|and|nand|not|xor|xnor) \S+\s*\((.+?)\);',data):
		nets |= set(m.replace(' ','').split(','))
	nets = list(nets)
	print(nets)


	# iterate over all input values
	for vals in product(range(2),repeat=len(inps)):
		print(vals)

		# simulate input
		inp_str = '\n'.join([f'force {inp} 1\'b{bit}' for inp,bit in zip(inps,vals)])
		net_str = '\n'.join([f'lappend net_vals [value %b {net}]' for net in nets])
		tcl = inp_str + '\nrun\n' + net_str +'\nputs [open net_vals w] $net_vals\nexit\n'
		with open('test.tcl','w') as f: f.write(tcl)
		subprocess.run(f'xrun {sys.argv[1]} -input test.tcl -access +w'.split(' '))
		with open('net_vals','r') as f:
			data = f.read()
		sim_results = [out=='1' for out in data.replace('\n','').replace('1\'b','').split(' ')]
		print(sim_results)
		print(nets)

		# sat input
		constraints = {inp:bit for inp,bit in zip(inps,vals)}
		print(constraints)
		cons_clauses = constrain(constraints,net_map,clauses)
		print(net_map)
		print(f'clauses: {clauses}')
		print(f'cons_clauses: {cons_clauses}')
		write(top,net_map,cons_clauses)
		try:
			data = subprocess.check_output(f'cadical {top}.dimacs'.split(' '))
		except subprocess.CalledProcessError as exc:
			data = exc.output
		print(data.decode('utf-8'))
		results = re.search('\nv (.+?) 0',data.decode('utf-8')).group(1)
		enc_sat_results = results.split(' ')
		print(enc_sat_results)
		sat_results = [int(enc_sat_results[net_map[net]-1])>0 for net in nets]

		print(nets)
		print(sat_results)
		print(sim_results)

		# compare
		if any(sim!=sat for sim,sat in zip(sim_results,sat_results)):
			print('ERROR')
			exit(1)

	print('Passed check')


def init_conditions_list_from_file(cur_instance, data):
    parsed_init_conditions = []
    with open(cur_instance, 'r') as file:
        lines = file.readlines()
        for i, line in enumerate(lines):
            if line.startswith('(:objects'):
                for j in range(i, len(lines)):
                    if lines[j].startswith('(:goal'):
                        break
                    
                    #split by spaces
                    chunked_line = lines[j].split(' ')
                    #iterate over chunks
                    #if the first element is a letter and the length of the string is at most 2, then it is an object
                    for k, chunk in enumerate(chunked_line):
                        if chunk[0].isalpha() and (len(chunk) <= 1 or chunk[1] == ')'):
                            #replace the chunk with the corresponding object
                            chunked_line[k] = data['encoded_objects'][chunk[0]].split(' ')[0] + chunk[1:]
                    #join the chunks back together
                    lines[j] = ' '.join(chunked_line)
                    parsed_init_conditions.append(lines[j])
                    
    parsed_init_conditions = [line.strip() for line in parsed_init_conditions]
    parsed_init_conditions = [line for line in parsed_init_conditions if line != '']
    return parsed_init_conditions


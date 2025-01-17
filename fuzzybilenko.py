import sys
import dedupe
import colorama

def setup(fields1, fields2, threshold):
    def executor(data1, data2):
        input1 = {i: {fields1[j]: value for j, value in enumerate(row)} for i, row in enumerate(data1)}
        input2 = {i: {fields1[j]: value for j, value in enumerate(row)} for i, row in enumerate(data2)}
        fields = [{'field': field, 'type': 'String'} for field in fields1]
        linker = dedupe.RecordLink(fields)
        linker.prepare_training(input1, input2, sample_size=1500)
        while True:
            labelling(linker)
            try:
                linker.train()
                break
            except: sys.stderr.write('\nYou need to do more training.\n')
        pairs = linker.join(input1, input2, threshold, 'many-to-many')
        matches = []
        for pair in pairs:
            matches.append((pair[0][0], pair[0][1], pair[1]))
        return matches
    return executor

def labelling(linker):
    colorama.init()
    sys.stderr.write('\n' + colorama.Style.BRIGHT + colorama.Fore.BLUE + 'Answer questions as follows:\n y - yes\n n - no\n s - skip\n f - finished' + colorama.Style.RESET_ALL + '\n')
    labels = { 'distinct': [], 'match': [] }
    finished = False
    while not finished:
        for pair in linker.uncertain_pairs():
            if pair[0] == pair[1]: # if they are exactly the same, presume a match
                labels['match'].append(pair)
                continue
            for record in pair:
                sys.stderr.write('\n')
                for field in set(field.field for field in linker.data_model.primary_fields):
                    sys.stderr.write(colorama.Style.BRIGHT + field + ': ' + colorama.Style.RESET_ALL + record[field] + '\n')
            sys.stderr.write('\n')
            responded = False
            while not responded:
                sys.stderr.write(colorama.Style.BRIGHT + colorama.Fore.BLUE + 'Do these records refer to the same thing? [y/n/s/f]' + colorama.Style.RESET_ALL + ' ')
                response = input()
                responded = True
                if   response == 'y': labels['match'].append(pair)
                elif response == 'n': labels['distinct'].append(pair)
                elif response == 's': continue
                elif response == 'f': finished = True
                else: responded = False
    linker.mark_pairs(labels)

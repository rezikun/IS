import re

# Parse template line into tokens
def tokenize(expected_line):
    tokens = re.findall('\[[^\]]*\]|\([^\)]*\)|\{[^\}]*\}|\S+', expected_line)
    # Extract multichoice tokens
    tokens[:] = [token[1:len(token) - 1].split('|') if token[0] == '[' else token for token in tokens]
    return tokens

# Tries to apply template line to the user input
def rec_matches(tokens, line, start, current_pos):
    saved_chunks = []
    for i in range(start, len(tokens)):
        if current_pos >= len(line):
            break

        # multiple choice token
        if isinstance(tokens[i], list):
            at_least_one_match = False
            for one_token in tokens[i]:
                if line[current_pos:current_pos + len(one_token)] == one_token:
                    at_least_one_match = True
                    current_pos += len(one_token) + 1
                    break
            if not at_least_one_match:
                return False, saved_chunks
        # wildcard token
        elif tokens[i] == '{*}':
            for k in range(current_pos, len(line)):
                match = rec_matches(tokens, line, i + 1, k)
                if match:
                    current_pos = k + 1
                    break
        # wildcard token with saving
        elif tokens[i] == '{w}':
            for k in range(current_pos, len(line)):
                match = rec_matches(tokens, line, i + 1, k)
                if match:
                    current_pos = k + 1
                    saved_chunks.append(line[current_pos-1:current_pos + k+1])
                    break
        else:
            if line[current_pos:current_pos + len(tokens[i])] != tokens[i]:
                return False, saved_chunks
            current_pos += len(tokens[i]) + 1
    return True, saved_chunks

def matches(expected_line, line):
    match, _ = rec_matches(tokenize(expected_line), line, 0, 0)
    return match


# parses user input and looks for parts of message that can be used in the answer
def build_answer(expected_line, template_answer, line):
    match, chunks = rec_matches(tokenize(expected_line), line, 0, 0)
    if not match:
        return 'Violence is not an answer!'
    answer = ''
    current_chunk = 0
    i = 0
    while i < len(template_answer) :
        if template_answer[i] == '{':
            for j in range(len(chunks[current_chunk])):
                answer += chunks[current_chunk][j]
            i += 3
            current_chunk += 1
        else:
            answer += template_answer[i]
            i += 1
    return answer


def parse_rule(rule):
    split = rule.split(' > ')
    return split[0], split[1]


def find_answer(line):
    with open("dialugue schema.txt", "r") as file_content:
        rules = file_content.readlines()
        for rule in rules:
            expected_line, answer = parse_rule(rule)
            if matches(expected_line.lower(), line.lower()):
                return build_answer(expected_line.lower(), answer, line.lower())
    return 'Roses are red'


def reply_to(line):
    reply = find_answer(line)
    print(reply)


if __name__ == '__main__':
    while True:
        line = input()
        if line == 'stop':
            break
        reply_to(line)

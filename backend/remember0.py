def split_and_join(line):
    return '-'.join(line.split())
if __name__ == '__main__':
    line = input()
    result = split_and_join(line)
    print(result)
# Input (stdin)
#     this is a string
# Your Output (stdout)
#     this-is-a-string



def print_full_name(first, last):
    print(f"Hello {first} {last}! You just delved into python.")
if __name__ == '__main__':
    first_name = input()
    last_name = input()
    print_full_name(first_name, last_name)
# Input (stdin)
#     Ross
#     Taylor
# Expected Output
#     Hello Ross Taylor! You just delved into python.
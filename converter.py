from argparse import ArgumentParser
import csv, sys, itertools, os, pickle

card_list = {}
filename = ""
filename_ext = ""
list_b = []

def quit_(code):
  print("Press enter to quit")
  input()
  sys.exit(code)

def read_db():
  global card_list
  # Open DB
  try:
    with open('list.db', 'r', newline='', encoding='utf-8') as db_file:
      reader = csv.reader(db_file)
      # Save card number into dictionary
      for row in reader:
        card_list[row[2]] = 0
  except FileNotFoundError:
    print("Make sure there is a 'list.db' file")
    quit_(1)
  return

def read_src(filename):
  list_ = []
  try:
    with open(filename, 'r') as f:
      for line in f:
        if line.strip():
          list_.append(line.strip())
  except FileNotFoundError:
    print("File", filename, "does not exist")
    quit_(1)
  return list_

def list_pair(list_):
  this_, next_ = itertools.tee(list_)
  next(next_, None)
  return zip(this_, next_)

def check_dup(pair):
  if(pair[0][2:10] == pair[1][2:10] and pair[0][23] == pair[1][23]):
    print("[INFO]    ID:", pair[0][2:10], "has two", pair[0][23], "records and is fixed")
    return True
  else:
    return False

def save_file(list_, name):
  with open(filename + name + filename_ext, 'w') as f:
    for line in list_:
      f.write("%s\n" % line)
  return

def phase1(list_):
  # Remove duplicate entry
  return [ pair[0] for pair in list_pair(list_) if not check_dup(pair) ]

def phase2(list_):
  # Set 0745 A and prior to 0746 A
  for idx, line in enumerate(list_):
    # Ignore the rest of the file
    if(line[23] != 'A'):
      break
    if(int(line[11:15]) <= 745):
      print("[INFO]    ID:", line[2:10], "A record is set to 0746")
      list_[idx] = line[0:11] + "0746" + line[15:] 
  return list_

def phase3(list_):
  global list_b
  # Save GHIJ to another list
  list_a = []
  for line in list_:
    if(line[23] == 'G' or
       line[23] == 'H' or
       line[23] == 'I' or
       line[23] == 'J'
      ):
      list_b.append(line)
    else:
      list_a.append(line)
  save_file(list_b, 'B')
  print("[INFO]    B list created")
  return list_a

def phase4(list_):
  # 1931~ E to F
  for idx, line in enumerate(list_):
    if(line[23] == 'E' and int(line[11:15]) >= 1931):
      print("[INFO]    ID:", line[2:10], line[11:15], "E record set to F")
      list_[idx] = line[0:23] + 'F' + line[24:]
  return list_

def phase5(list_):
  global card_list
  for idx, line in enumerate(list_):
    if(line[2:10] in card_list and line[23] == 'F' and (1855 <= int(line[11:15]) <= 1905)):
      print("[INFO]    ID:", line[2:10], "F changed from", line[11:15], "to", int(line[11:15]) + 30)
      list_[idx] = line[0:11] + str(int(line[11:15]) + 30) + line[15:]
  save_file(list_, 'A')
  return list_

def phasen(list_):
  global list_b
  list_ += list_b
  # Sanity check
  total = {}
  # Get total count
  for line in list_:
    if not line[2:10] in total:
      total[line[2:10]] = 1
    else:
      total[line[2:10]] += 1
  # Record count is even number
  for item, value in total.items():
    if value % 2 != 0:
      print("[Warning] ID:", item, "only has", value, "records after correction")
  return list_

def main():
  global filename
  global filename_ext
  read_db()
  # Get filename
  parser = ArgumentParser()
  parser.add_argument("file")
  filename, filename_ext = os.path.splitext(parser.parse_args().file)
  phasen(phase5(phase4(phase3(phase2(phase1(read_src(parser.parse_args().file)))))))
  quit_(0)

if __name__ == '__main__':
  main()

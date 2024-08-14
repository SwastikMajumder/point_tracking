from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel


app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>math Ai</title>
    </head>
    <body>
        <h1>solve the math equation</h1>
        <form id="input-form">
            <label for="input_string">enter equation in string format</label><br>
            <textarea id="input_string" name="input_string" placeholder="type here..."></textarea><br>
            <button type="button" onclick="submitInput()">Submit</button>
        </form>
        <div id="output"></div>

        <script>
            function submitInput() {
                const form = document.getElementById('input-form');
                const formData = new FormData(form);

                fetch('/process/', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    document.getElementById('output').innerHTML = '<pre>' + data.result + '</pre>';
                })
                .catch(error => {
                    console.error('Error:', error);
                    document.getElementById('output').innerHTML = '<pre>Error: ' + error + '</pre>';
                });
            }
        </script>
    </body>
    </html>
    '''

import copy
from lark import Lark, Tree


# Basic data structure, which can nest to represent math equations
class TreeNode:
    def __init__(self, name, children=None):
        self.name = name
        self.children = children or []

# convert string representation into tree
def tree_form(tabbed_strings):
    lines = tabbed_strings.split("\n")
    root = TreeNode("Root") # add a dummy node
    current_level_nodes = {0: root}
    stack = [root]
    for line in lines:
        level = line.count(' ') # count the spaces, which is crucial information in a string representation
        node_name = line.strip() # remove spaces, when putting it in the tree form
        node = TreeNode(node_name)
        while len(stack) > level + 1:
            stack.pop()
        parent_node = stack[-1]
        parent_node.children.append(node)
        current_level_nodes[level] = node
        stack.append(node)
    return root.children[0] # remove dummy node

# convert tree into string representation
def str_form(node):
    def recursive_str(node, depth=0):
        result = "{}{}".format(' ' * depth, node.name) # spacings
        for child in node.children:
            result += "\n" + recursive_str(child, depth + 1) # one node in one line
        return result
    return recursive_str(node)

# Define the grammar for simple arithmetic expressions
grammar = """
?start: expr

?expr: term
     | expr "+" term   -> add
     | expr "-" term   -> sub

?term: factor
     | term "*" factor  -> mul
     | term "/" factor  -> div

?factor: base
       | factor "^" base  -> pow

?base: NUMBER            -> number
     | FUNC_NAME "(" expr ")" -> func
     | VARIABLE          -> variable
     | "(" expr ")"      -> paren

FUNC_NAME: "sin" | "cos" | "tan" | "log" | "sqrt"
VARIABLE: "x" | "y" | "z"

%import common.NUMBER
%import common.WS_INLINE
%ignore WS_INLINE
"""

# Create a parser
parser = Lark(grammar, start='start', parser='lalr')

# Example equation to parse
def take_input(equation):#"sin(3)+1+2"

  # Parse the equation
  parse_tree = parser.parse(equation)

  def convert_to_treenode(parse_tree):
      def tree_to_treenode(tree):
          if isinstance(tree, Tree):
              node = TreeNode(tree.data)
              node.children = [tree_to_treenode(child) for child in tree.children]
              return node
          else:  # Leaf node
              return TreeNode(str(tree))

      return tree_to_treenode(parse_tree)

  # fancy print
  def string_equation_helper(equation_tree):
      if equation_tree.children == []:
          return equation_tree.name # leaf node
      s = "(" # bracket
      if len(equation_tree.children) == 1:
          s = equation_tree.name[2:] + s
      sign = {"f_add": "+", "f_mul": "*", "f_pow": "^", "f_div": "/", "f_int": ",", "f_sub": "-", "f_dif": "?", "f_sin": "?", "f_cos": "?", "f_tan": "?", "f_eq": "=", "f_sqt": "?"} # operation symbols
      for child in equation_tree.children:
          s+= string_equation_helper(copy.deepcopy(child)) + sign[equation_tree.name]
      s = s[:-1] + ")"
      return s

  # fancy print main function
  def string_equation(eq): 
      eq = eq.replace("v_0", "x")
      eq = eq.replace("v_1", "y")
      eq = eq.replace("v_2", "z")
      eq = eq.replace("d_", "")
      
      return string_equation_helper(tree_form(eq))

  def replace(equation, find, r):
    if str_form(equation) == str_form(find):
      return r
    col = TreeNode(equation.name, [])
    for child in equation.children:
      col.children.append(replace(child, find, r))
    return col
  def remove_past(equation):
      if equation.name in {"number", "paren", "func", "variable"}:
          if len(equation.children) == 1:
            for index, child in enumerate(equation.children):
              equation.children[index] = remove_past(child)
            return equation.children[0]
          else:
            for index, child in enumerate(equation.children):
              equation.children[index] = remove_past(child)
            return TreeNode(equation.children[0].name, equation.children[1:])
      coll = TreeNode(equation.name, [])
      for child in equation.children:
          coll.children.append(remove_past(child))
      return coll
  # Convert and print TreeNode structure
  tree_node = convert_to_treenode(parse_tree)
  tree_node = remove_past(tree_node)
  tree_node = str_form(tree_node)
  #print(tree_node)
  for item in ["add", "sin", "cos", "tan", "mul", "pow", "div"]:
    tree_node = tree_node.replace(str(item), "f_" + str(item))
  tree_node = tree_form(tree_node)
  for i in range(100,-1,-1):
    tree_node = replace(tree_node, tree_form(str(i)), tree_form("d_"+str(i)))
  for i in range(3):
    tree_node = replace(tree_node, tree_form(["x", "y", "z"][i]), tree_form("v_"+str(i)))
  tree_node = str_form(tree_node)
  return tree_node


high_main = """f_add
 u_0
 d_0

u_0

f_mul
 u_0
 d_1

u_0

f_mul
 u_0
 u_0

f_pow
 u_0
 d_2

f_add
 u_0
 u_0

f_mul
 d_2
 u_0

f_add
 f_mul
  u_0
  d_-1
 u_0

d_0

f_add
 f_pow
  f_sin
   u_0
  d_2
 f_pow
  f_cos
   u_0
  d_2

d_1

f_div
 f_div
  u_0
  u_1
 u_2

f_div
 u_0
 f_mul
  u_1
  u_2

f_div
 f_mul
  u_0
  u_1
 u_1

u_0

f_div
 u_0
 u_0

d_1

f_div
 f_pow
  u_0
  p_0
 u_0

f_pow
 u_0
 f_add
  p_0
  d_-1

f_pow
 u_0
 d_1

u_0"""

low_main = """f_add
 u_0
 u_1

f_add
 u_1
 u_0

f_mul
 u_0 
 u_1

f_mul
 u_1
 u_0

f_mul
 u_0
 f_mul
  u_1
  u_2

f_mul
 u_1
 f_mul
  u_0
  u_2

f_add
 u_0
 f_add
  u_1
  u_2

f_add
 u_1
 f_add
  u_0
  u_2"""

medium_main = """f_mul
 u_0
 f_add
  u_1
  u_2

f_add
 f_mul
  u_0
  u_1
 f_mul
  u_0
  u_2

f_add
 u_0
 f_div
  u_1
  u_2

f_div
 f_add
  f_mul
   u_0 
   u_2
  u_1
 u_2

f_mul
 u_0
 f_div
  u_1
  u_2

f_div
 f_mul
  u_0
  u_1
 u_2

f_div
 f_add
  u_0
  u_1
 u_2

f_add
 f_div
  u_0
  u_2
 f_div
  u_1
  u_2

f_add
 u_0
 f_mul
  p_0
  u_0

f_mul
 f_add
  p_0
  d_1
 u_0

f_mul
 u_0
 f_pow
  u_0
  p_0

f_pow
 u_0
 f_add
  p_0
  d_1

f_pow
 f_pow
  u_0
  p_0
 p_1

f_pow
 u_0
 f_mul
  p_0
  p_1

f_mul
 f_pow
  u_0
  p_0
 f_pow
  u_0
  p_1

f_pow
 u_0
 f_add
  p_0
  p_1"""

# Generate transformations of a given equation provided only one formula to do so
# We can call this function multiple times with different formulas, in case we want to use more than one
# This function is also responsible for computing arithmetic, pass do_only_arithmetic as True (others param it would ignore), to do so
def apply_individual_formula_on_given_equation(equation, formula_lhs, formula_rhs, do_only_arithmetic=False, structure_satisfy=False):
    variable_list = {}
    
    def node_type(s):
        if s[:2] == "f_":
            return s
        else:
            return s[:2]
    def does_given_equation_satisfy_forumla_lhs_structure(equation, formula_lhs):
        nonlocal variable_list
        # u can accept anything and p is expecting only integers
        # if there is variable in the formula
        if node_type(formula_lhs.name) in {"u_", "p_"}: 
            if formula_lhs.name in variable_list.keys(): # check if that variable has previously appeared or not
                return str_form(variable_list[formula_lhs.name]) == str_form(equation) # if yes, then the contents should be same
            else: # otherwise, extract the data from the given equation
                if node_type(formula_lhs.name) == "p_" and "v_" in str_form(equation): # if formula has a p type variable, it only accepts integers
                    return False
                variable_list[formula_lhs.name] = copy.deepcopy(equation)
                return True
        if equation.name != formula_lhs.name or len(equation.children) != len(formula_lhs.children): # the formula structure should match with given equation
            return False
        for i in range(len(equation.children)): # go through every children and explore the whole formula / equation
            if does_given_equation_satisfy_forumla_lhs_structure(equation.children[i], formula_lhs.children[i]) is False:
                return False
        return True
    if structure_satisfy:
      return does_given_equation_satisfy_forumla_lhs_structure(equation, formula_lhs)
    # transform the equation as a whole aka perform the transformation operation on the entire thing and not only on a certain part of the equation
    def formula_apply_root(formula):
        nonlocal variable_list
        if formula.name in variable_list.keys():
            return variable_list[formula.name] # fill the extracted data on the formula rhs structure
        data_to_return = TreeNode(formula.name, None) # produce nodes for the new transformed equation
        for child in formula.children:
            data_to_return.children.append(formula_apply_root(copy.deepcopy(child))) # slowly build the transformed equation
        return data_to_return
    count_target_node = 1
    # try applying formula on various parts of the equation
    def formula_apply_various_sub_equation(equation, formula_lhs, formula_rhs, do_only_arithmetic):
        nonlocal variable_list
        nonlocal count_target_node
        data_to_return = TreeNode(equation.name, children=[])
        variable_list = {}
        if do_only_arithmetic == False:
            if does_given_equation_satisfy_forumla_lhs_structure(equation, copy.deepcopy(formula_lhs)) is True: # if formula lhs structure is satisfied by the equation given
                count_target_node -= 1
                if count_target_node == 0: # and its the location we want to do the transformation on
                    return formula_apply_root(copy.deepcopy(formula_rhs)) # transform
        else: # perform arithmetic
            if len(equation.children) == 2 and all(node_type(item.name) == "d_" for item in equation.children): # if only numbers
                x = []
                for item in equation.children:
                    x.append(int(item.name[2:])) # convert string into a number
                if equation.name == "f_add":
                    count_target_node -= 1
                    if count_target_node == 0: # if its the location we want to perform arithmetic on
                        return TreeNode("d_" + str(sum(x))) # add all
                elif equation.name == "f_mul":
                    count_target_node -= 1
                    if count_target_node == 0:
                        p = 1
                        for item in x:
                            p *= item # multiply all
                        return TreeNode("d_" + str(p))
                elif equation.name == "f_pow" and x[1]>=2: # power should be two or a natural number more than two
                    count_target_node -= 1
                    if count_target_node == 0:
                        return TreeNode("d_"+str(int(x[0]**x[1])))
        if node_type(equation.name) in {"d_", "v_"}: # reached a leaf node
            return equation
        for child in equation.children: # slowly build the transformed equation
            data_to_return.children.append(formula_apply_various_sub_equation(copy.deepcopy(child), formula_lhs, formula_rhs, do_only_arithmetic))
        return data_to_return
    cn = 0
    # count how many locations are present in the given equation
    def count_nodes(equation):
        nonlocal cn
        cn += 1
        for child in equation.children:
            count_nodes(child)
    transformed_equation_list = []
    count_nodes(equation)
    for i in range(1, cn + 1): # iterate over all location in the equation tree
        count_target_node = i
        orig_len = len(transformed_equation_list)
        tmp = formula_apply_various_sub_equation(equation, formula_lhs, formula_rhs, do_only_arithmetic)
        if str_form(tmp) != str_form(equation): # don't produce duplication, or don't if nothing changed because of transformation impossbility in that location
            transformed_equation_list.append(str_form(tmp)) # add this transformation to our list
    return transformed_equation_list 

# Function to generate neighbor equations
def generate_transformation(equation, file_name):
    input_f, output_f = return_formula_file(file_name) # load formula file
    transformed_equation_list = []
    for i in range(len(input_f)): # go through all formulas and collect if they can possibly transform
        transformed_equation_list += apply_individual_formula_on_given_equation(tree_form(copy.deepcopy(equation)), copy.deepcopy(input_f[i]), copy.deepcopy(output_f[i]))
    return list(set(transformed_equation_list)) # set list to remove duplications

# Function to generate neighbor equations
def generate_arithmetical_transformation(equation):
    transformed_equation_list = []
    transformed_equation_list += apply_individual_formula_on_given_equation(tree_form(equation), None, None, True) # perform arithmetic
    return list(set(transformed_equation_list)) # set list to remove duplications

# Function to read formula file
def return_formula_file(file_name):
    global high_main
    global medium_main
    global low_main
    if file_name == "high-main.txt":
      x = high_main
    elif file_name == "medium-main.txt":
      x = medium_main
    else:
      x = low_main
    x = x.split("\n\n")
    input_f = [x[i] for i in range(0, len(x), 2)] # alternative formula lhs and then formula rhs
    output_f = [x[i] for i in range(1, len(x), 2)]
    input_f = [tree_form(item) for item in input_f] # convert into tree form
    output_f = [tree_form(item) for item in output_f]
    return [input_f, output_f] # return

def search(equation, depth, file_list, auto_arithmetic=True, visited=None):
    if depth == 0: # limit the search
        return None
    if visited is None:
        visited = set()

    #print(string_equation(equation))
    if equation in visited:
        return None
    visited.add(equation)
    output =[]
    if file_list[0]:
      output += generate_transformation(equation, file_list[0])
    if auto_arithmetic:
      output += generate_arithmetical_transformation(equation)
    if len(output) > 0:
      output = [output[0]]
    else:
      if file_list[1]:
        output += generate_transformation(equation, file_list[1])
      if not auto_arithmetic:
        output += generate_arithmetical_transformation(equation)
      if file_list[2] and len(output) == 0:
          output += generate_transformation(equation, file_list[2])
    for i in range(len(output)):
        result = search(output[i], depth-1, file_list, auto_arithmetic, visited) # recursively find even more equals
        if result is not None:
            output += result # hoard them
    output = list(set(output))
    return output

# fancy print
def string_equation_helper(equation_tree):
    if equation_tree.children == []:
        return equation_tree.name # leaf node
    s = "(" # bracket
    if len(equation_tree.children) == 1:
        s = equation_tree.name[2:] + s
    sign = {"f_add": "+", "f_mul": "*", "f_pow": "^", "f_div": "/", "f_int": ",", "f_sub": "-", "f_dif": "?", "f_sin": "?", "f_cos": "?", "f_tan": "?", "f_eq": "=", "f_sqt": "?"} # operation symbols
    for child in equation_tree.children:
        s+= string_equation_helper(copy.deepcopy(child)) + sign[equation_tree.name]
    s = s[:-1] + ")"
    return s

# fancy print main function
def string_equation(eq): 
    eq = eq.replace("v_0", "x")
    eq = eq.replace("v_1", "y")
    eq = eq.replace("v_2", "z")
    eq = eq.replace("d_", "")
    
    return string_equation_helper(tree_form(eq))

def replace(equation, find, r):
  if str_form(equation) == str_form(find):
    return r
  col = TreeNode(equation.name, [])
  for child in equation.children:
    col.children.append(replace(child, find, r))
  return col

def process_input(string_input):
    eq = take_input(string_input)
    init = eq
    #print(eq)
    for _ in range(3):
        orig = eq
        eq = sorted(search(eq, 7, ["high-main.txt", "medium-main.txt", "low-main.txt"]), key=lambda x: len(string_equation(x))-len(set(string_equation(x))))
        if eq:
            eq = eq[0]
            if eq == orig:
                break
        else:
            eq = orig
            break
        #print("re-centering")
    #eq = sorted(search(eq, 10, ["formula-list/high-main.txt", "formula-list/medium-main.txt", "formula-list/low-main.txt"]), key=lambda x: len(x))[0]
    return "Ai says that " + string_equation(init) + " is equal to " + string_equation(eq)


@app.post("/process/")
async def process_request(input_string: str = Form(...)):
    result = process_input(input_string)  # Call the function from script.py
    return {"result": result}

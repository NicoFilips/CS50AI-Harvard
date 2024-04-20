import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        # Iterate through each variable in the original domains
        for variable in list(self.domains):
            # Get the required length of the word for this variable
            length = variable.length
            # Create a new list with only words of the correct length
            new_domain = [word for word in self.domains[variable] if len(word) == length]
            # Update the domain of the variable with the filtered list
            self.domains[variable] = new_domain

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.
        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        xoverlap, yoverlap = self.crossword.overlaps[x, y]
        revision_made = False
        if xoverlap:
            new_domain = []
            for xword in self.domains[x]:
                if any(xword[xoverlap] == yword[yoverlap] for yword in self.domains[y]):
                    new_domain.append(xword)
                else:
                    revision_made = True
            if revision_made:
                self.domains[x] = new_domain
        return revision_made

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is None:
            arcs = []
            for var1 in self.domains:
                for var2 in self.crossword.neighbors(var1):
                    if var1 != var2:
                        arcs.append((var1, var2))

        while arcs:
            var1, var2 = arcs.pop(0)  # Pop from start of the list
            if self.revise(var1, var2):
                if len(self.domains[var1]) == 0:
                    return False
                for neighbor in self.crossword.neighbors(var1):
                    if neighbor != var2:
                        arcs.append((neighbor, var1))  # Add to end of the list

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        return len(self.domains) == len(assignment)


    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        value_set = set()
        for var, value in assignment.items():
            if value in value_set:
                return False
            value_set.add(value)
   
            # Check if word length matches the variable's requirement
            if len(value) != var.length:
                return False
   
            # Check for conflicts between assigned neighbors
            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                    index_var, index_neighbor = self.crossword.overlaps[var, neighbor]
                    if value[index_var] != assignment[neighbor][index_neighbor]:
                        return False
            return True

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.
            
        `assignment` is a mapping from variables (keys) to words (values).
            
        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment

        var = self.select_unassigned_variable(assignment)

        for value in self.order_domain_values(var, assignment):

            assignment[var] = value

            if self.consistent(assignment):
                self.ac3()
                result = self.backtrack(assignment)
                if result is not None:
                    return result

            assignment.pop(var)
            
        return None

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        rule_out = {}
        neighbors = [neighbor for neighbor in self.crossword.neighbors(var) if neighbor not in assignment]
    
        for value in self.domains[var]:
            rule_out[value] = 0
    
            for neighbor in neighbors:
                overlap = self.crossword.overlaps[var, neighbor]
                conflicting_values = sum(
                    1 for word in self.domains[neighbor] if value[overlap[0]] != word[overlap[1]]
                )
                rule_out[value] += conflicting_values
    
        return sorted(rule_out, key=rule_out.get)

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        candidate = None
        min_domain_size = float('inf')
        max_degree = -1
   
        for var in self.domains:
            if var not in assignment:
                domain_size = len(self.domains[var])
                degree = len(self.crossword.neighbors(var))
   
                if (domain_size < min_domain_size) or (domain_size == min_domain_size and degree > max_degree):
                    candidate = var
                    min_domain_size = domain_size
                    max_degree = degree
   
        return candidate

def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()

import math
from hexalattice.hexalattice import *
import matplotlib.pyplot as plt
import sys
import random

SIZE = 61
TEST_MODE = False  # if True than a comparison between shuffled SOM and un-shuffled SOM will be displayed
# COLORS
main_colors = ['w', 'k', 'r', 'b', 'g', 'y', 'c']  # only works for the first initiation canvas
all_black = np.zeros([SIZE, 3])  # to paint all cells or edges in black
all_white = np.ones([SIZE, 3])  # to paint all cells or edges in white
white = [1, 1, 1]  # single cell in white
black = [0, 0, 0]  # single cell in black
blue = [0, 0, 1]  # single cell in blue
green = [0, 1, 0]  # single cell in green
red = [1, 0, 0]  # single cell in red
grey = [0.5, 0.5, 0.5]  # single cell in grey
# green colors, the higher the number, dark green to light green:
c = [1, 0.75, 0]
c1 = [0, 0.1, 0]
c2 = [0, 0.2, 0]
c3 = [0, 0.3, 0]
c4 = [0, 0.4, 0]
c5 = [0, 0.5, 0]
c6 = [0, 0.6, 0]
c7 = [0, 0.7, 0]
c8 = [0, 0.8, 0]
c9 = [0, 0.9, 0]
c10 = [0, 1, 0]
# this color list will be used to decide the hexagon color, higher number => higher eco cluster => brighter color
colors = [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10]

location_color_list = np.ones([SIZE, 3])  # all the cells will be white

# UPDATED AFTER HEXAGONS LATTICE INITIATION:
cell_locations = []  # will get the "real" locations in initiation
xCoordsArray = []
yCoordsArray = []

# DICTIONARIES:
cell_vector_scores = {}  # key will be location, value will be the calculated score from the random vector
input_vector_scores = {}  # key = (Municipality, Economic Cluster) : value = calculated score from the the vector
cell_neighbors = {}  # key will be the cell index, value will be a list for his 1st degree neighbors

# FINAL SOM
SOM_options = {}  # 10 different SOMs, we will choose the one with the lowest error and display it at the end
SOM_city_lists = {}


def main():
    global cell_locations
    global xCoordsArray
    global yCoordsArray
    # initiate Hexagon pattern with 61 blank cells:
    hex_centers, h_ax = create_hex_grid(n=100, min_diam=1, align_to_origin=True, crop_circ=4, face_color=all_white)
    cell_locations = hex_centers  # initiate locations list
    xCoordsArray = np.array([x[0] for x in hex_centers])
    yCoordsArray = np.array([x[1] for x in hex_centers])
    # initiate neighbors dictionary for each cell:
    initiate_neighbors()
    # load the .csv file (this is also going to initialize the input_vectors dictionary)
    load_file()
    # create 10 different SOMs and choose the SOM with the lowest error (QE & TE)
    for i in range(10):
        # generate random score values for each cell
        for loc in range(SIZE):
            cell_vector_scores[loc] = generate_random_score_for_each_hexagonal_cell()
        if TEST_MODE:  # execute this only if TEST_MODE == True
            generate_SOM()  # add new SOM to the SOM_options dictionary
            generate_SOM(shuffle=True)
            print("original city order SOM error =", list(SOM_options.keys())[0])
            display_SOM(list(SOM_options.values())[0])  # Figure 1
            print("shuffled city order SOM error =", list(SOM_options.keys())[1])
            display_SOM(list(SOM_options.values())[1])  # Figure 2
            plt.show()
            quit()

        generate_SOM(shuffle=True)  # add new SOM to the SOM_options dictionary

    # find the minimum score from all 10 SOMs:
    minimum_SOM_error = min(SOM_options.keys())
    # choose the color pattern for the "best" SOM (according to the minimum score):
    minimum_error_SOM_color_map = SOM_options[minimum_SOM_error]
    # choose the cities distribution for the "best" SOM (according to the minimum score):
    minimum_error_SOM_city_to_hexagon_distribution = SOM_city_lists[minimum_SOM_error]
    # print the city to hexagon cell list:
    print_hexagon_index_city_list(minimum_error_SOM_city_to_hexagon_distribution)
    # display the final result
    display_SOM(minimum_error_SOM_color_map)


# FUNCTIONS:

def display_SOM(color_map):
    plot_single_lattice_custom_colors(xCoordsArray, yCoordsArray, face_color=color_map,
                                      edge_color=all_black, min_diam=1, plotting_gap=0, rotate_deg=0)
    if not TEST_MODE:
        # save SOM as .png
        plt.savefig("SOM.png")
        # display SOM figure
        plt.show()


def to_vec(int_array):  # transforms array to into a vector
    vec = np.zeros(15)
    for i in range(15):
        vec[i] = int_array[i]
    return vec


def load_file():  # load the .csv file and create the input_vector_scores dictionary
    global input_vector_scores
    f = open(sys.argv[1])
    lines = f.readlines()  # read all file line
    for line in lines[1:-1]:
        line = line.split(",")
        key = (line[0], int(line[1]))
        int_arr = [int(numeric_string) for numeric_string in line[1:]]
        vec = to_vec(int_arr)
        score = get_score(vec)
        input_vector_scores[key] = score


def get_score(vector):  # generate a score for the vector based on its values
    # vector must be size 15
    vec = np.zeros(14)  # new vector size 14
    vec[13] = vector[0] * 100
    # calculate percentage for all parties in relation to the amount of voters in that city
    vec[0] = vector[2] / vector[1] * 100 * 2  # Labour
    vec[1] = vector[3] / vector[1] * 100 * 3  # Yamina
    vec[2] = vector[4] / vector[1] * 100 * 3.500  # Yahadot Hatora
    vec[3] = vector[5] / vector[1] * 100 * 1  # The Joint Party
    vec[4] = vector[6] / vector[1] * 100 * 3  # Zionut Datit
    vec[5] = vector[7] / vector[1] * 100 * 2.5  # Kachul Lavan
    vec[6] = vector[8] / vector[1] * 100 * 3  # Israel Betinu
    vec[7] = vector[9] / vector[1] * 100 * 4  # Licod
    vec[8] = vector[10] / vector[1] * 100 * 1.5  # Merez
    vec[9] = vector[11] / vector[1] * 100 * 1  # Raam
    vec[10] = vector[12] / vector[1] * 100 * 2.5  # Yesh Atid
    vec[11] = vector[13] / vector[1] * 100 * 3.5  # Shas
    vec[12] = vector[14] / vector[1] * 100 * 2.5  # Tikva Hadasha
    # calculate RMS (Root mean square) of all percentages and return the result
    RMS = np.sqrt(np.mean(vec ** 2))
    return math.floor(RMS)


def generate_random_score_for_each_hexagonal_cell():  # generate a new random vector for each hexagon cell
    # generate random vector and return his score (based on the .csv input)
    vec = np.zeros(15)
    vec[0] = random.randint(1, 10)  # Economic Cluster
    vec[1] = random.randint(562, 262696)  # Total Votes
    vec[2] = random.randint(1, vec[1])
    vec[3] = random.randint(0, vec[1] - vec[2])
    vec[4] = random.randint(0, vec[1] - vec[3])
    vec[5] = random.randint(0, vec[1] - vec[4])
    vec[6] = random.randint(0, vec[1] - vec[5])
    vec[7] = random.randint(0, vec[1] - vec[6])
    vec[8] = random.randint(0, vec[1] - vec[7])
    vec[9] = random.randint(17, vec[1] - vec[8])
    vec[10] = random.randint(0, vec[1] - vec[9])
    vec[11] = random.randint(0, vec[1] - vec[10])
    vec[12] = random.randint(0, vec[1] - vec[11])
    vec[13] = random.randint(0, vec[1] - vec[12])
    vec[14] = random.randint(0, vec[1] - vec[13])
    score = get_score(vec)
    return score


def generate_SOM(shuffle=False):
    SOM = np.ones([SIZE, 3])  # RGB color map size 61, all the cells will be initiated to be white
    cell_fitted_cities_SOM = {}  # will be used in the SOM
    cell_fitted_cities = {}  # will be added to the city lists
    for i in range(SIZE):
        cell_fitted_cities_SOM[i] = []  # list of fitted cities
    QE = 0  # Quantization Error (will be summed until the end and than average will be checked QE = QE / SIZE)
    TE = 0  # Topological Error
    cities = list(input_vector_scores.keys())
    if shuffle:  # shuffle=True
        random.shuffle(cities)
    for city in cities:  # find the "best fitted" cell for each city
        city_score = input_vector_scores[city]
        curr_shortest_dist = 1000
        curr_best_fitted_cell_index = 0  # will be updated to the best cell for current city
        curr_second_best_fitted_cell_index = 0  # will be checked if in the neighbors list
        for cell in cell_vector_scores:
            curr_dist = abs(city_score - cell_vector_scores[cell])
            if curr_dist < curr_shortest_dist:
                curr_shortest_dist = curr_dist
                curr_second_best_fitted_cell_index = curr_best_fitted_cell_index
                curr_best_fitted_cell_index = cell

        # check if curr_second_best_fitted_cell_index in the neighbors list of curr_best_fitted_cell_index
        QE += curr_shortest_dist
        if curr_second_best_fitted_cell_index not in set(cell_neighbors[curr_best_fitted_cell_index]):
            TE += 1
        #  connect the city to the best fitted hexagon cell (index)
        cell_fitted_cities_SOM[curr_best_fitted_cell_index].append(city[1])  # add the cities eco cluster group (1-10)
        cell_fitted_cities[city[0]] = curr_best_fitted_cell_index  # city name : cell index
        # update cells:
        # update score for curr_best_fitted_cell_index to make it closer to the city's score (30% closer):
        cell_vector_scores[curr_best_fitted_cell_index] = math.floor(0.7 * cell_vector_scores[curr_best_fitted_cell_index] + 0.3 * city_score)
        # update score for curr_best_fitted_cell_index neighbors to make it closer to the city's score (20% closer for all his neighbors):
        curr_neighbors = cell_neighbors[curr_best_fitted_cell_index]
        for neighbor_index in curr_neighbors:
            cell_vector_scores[neighbor_index] = math.floor(0.8 * cell_vector_scores[neighbor_index] + 0.2 * city_score)
            # 2nd degree neighbors:
            second_neighbors = cell_neighbors[neighbor_index]
            for second_neighbor_index in second_neighbors:  # check the current neighbor's neighbors
                if second_neighbor_index not in [curr_best_fitted_cell_index, neighbor_index]:
                    cell_vector_scores[second_neighbor_index] = math.floor(
                        0.9 * cell_vector_scores[second_neighbor_index] + 0.1 * city_score)

    error = QE / SIZE + TE
    # update SOM
    for index in cell_fitted_cities_SOM.keys():
        lst = cell_fitted_cities_SOM[index]
        if len(lst) > 0:
            curr_avg = math.floor(sum(lst) / len(lst))
            color_arr = colors[curr_avg - 1]  # generate color for this cell based on the eco cluster
            SOM[index] = color_arr  # the brighter the color the the higher the Economic Cluster's average score

    SOM_options[error] = SOM
    SOM_city_lists[error] = cell_fitted_cities


def print_hexagon_index_city_list(city_list_dict):
    f = open("Municipalities_distribution_in_SOM.txt", "w+")
    for index in range(SIZE):
        city_list = []
        for city in city_list_dict.keys():
            if city_list_dict[city] == index:
                city_list.append(city)
        print("hexagon index", index, "contains: ", city_list)
        s = (", ".join(city_list))
        string = "hexagon index " + str(index) + " contains: " + s + "\n"
        f.write(string)
    f.close()


def compare_city_order():
    generate_SOM()
    generate_SOM(shuffle=True)


def initiate_neighbors():  # key = location index : value = 1st degree neighbors index array
    global cell_neighbors
    cell_neighbors[0] = [5, 6, 1]
    cell_neighbors[1] = [0, 6, 7, 2]
    cell_neighbors[2] = [1, 7, 8, 3]
    cell_neighbors[3] = [2, 8, 9, 4]
    cell_neighbors[4] = [3, 9, 10]
    cell_neighbors[5] = [11, 12, 6, 0]
    cell_neighbors[6] = [5, 12, 13, 7, 1, 0]
    cell_neighbors[7] = [6, 13, 14, 8, 2, 1]
    cell_neighbors[8] = [7, 14, 15, 9, 3, 2]
    cell_neighbors[9] = [8, 15, 16, 10, 4, 3]
    cell_neighbors[10] = [9, 16, 17, 4]
    cell_neighbors[11] = [18, 19, 12, 5]
    cell_neighbors[12] = [11, 19, 20, 13, 6, 5]
    cell_neighbors[13] = [12, 20, 21, 14, 7, 6]
    cell_neighbors[14] = [13, 21, 22, 15, 8, 7]
    cell_neighbors[15] = [14, 22, 23, 16, 9, 8]
    cell_neighbors[16] = [15, 23, 24, 17, 10, 9]
    cell_neighbors[17] = [16, 24, 25, 10]
    cell_neighbors[18] = [26, 27, 19, 11]
    cell_neighbors[19] = [18, 27, 28, 20, 12, 11]
    cell_neighbors[20] = [19, 28, 29, 21, 13, 12]
    cell_neighbors[21] = [20, 29, 30, 22, 14, 13]
    cell_neighbors[22] = [21, 30, 31, 23, 15, 14]
    cell_neighbors[23] = [22, 31, 32, 24, 16, 15]
    cell_neighbors[24] = [23, 32, 33, 25, 17, 17]
    cell_neighbors[25] = [24, 33, 34, 17]
    cell_neighbors[26] = [35, 27, 18]
    cell_neighbors[27] = [26, 35, 36, 28, 19, 18]
    cell_neighbors[28] = [27, 36, 37, 29, 20, 19]
    cell_neighbors[29] = [28, 37, 38, 30, 21, 20]
    cell_neighbors[30] = [29, 38, 39, 31, 22, 21]
    cell_neighbors[31] = [30, 39, 40, 32, 23, 22]
    cell_neighbors[32] = [31, 40, 41, 33, 24, 23]
    cell_neighbors[33] = [32, 41, 42, 34, 25, 24]
    cell_neighbors[34] = [33, 42, 25]
    cell_neighbors[35] = [43, 36, 27, 26]
    cell_neighbors[36] = [35, 43, 44, 37, 28, 27]
    cell_neighbors[37] = [36, 44, 45, 38, 29, 28]
    cell_neighbors[38] = [37, 45, 46, 39, 30, 29]
    cell_neighbors[39] = [38, 46, 47, 40, 31, 30]
    cell_neighbors[40] = [39, 47, 48, 41, 32, 31]
    cell_neighbors[41] = [40, 48, 49, 42, 33, 32]
    cell_neighbors[42] = [41, 49, 34, 33]
    cell_neighbors[43] = [50, 44, 36, 35]
    cell_neighbors[44] = [43, 50, 51, 45, 37, 36]
    cell_neighbors[45] = [44, 51, 52, 46, 38, 37]
    cell_neighbors[46] = [45, 52, 53, 47, 39, 38]
    cell_neighbors[47] = [46, 53, 54, 48, 40, 39]
    cell_neighbors[48] = [47, 54, 55, 49, 41, 40]
    cell_neighbors[49] = [48, 55, 42, 41]
    cell_neighbors[50] = [56, 51, 44, 43]
    cell_neighbors[51] = [50, 56, 57, 52, 45, 44]
    cell_neighbors[52] = [51, 57, 58, 53, 46, 45]
    cell_neighbors[53] = [52, 58, 59, 54, 47, 46]
    cell_neighbors[54] = [53, 59, 60, 55, 48, 47]
    cell_neighbors[55] = [54, 60, 49, 48]
    cell_neighbors[56] = [57, 51, 50]
    cell_neighbors[57] = [56, 58, 52, 51]
    cell_neighbors[58] = [57, 59, 53, 52]
    cell_neighbors[59] = [58, 60, 54, 53]
    cell_neighbors[60] = [59, 55, 54]


if __name__ == '__main__':
    main()

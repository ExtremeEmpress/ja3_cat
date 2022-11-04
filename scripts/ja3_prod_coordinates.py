import ja3_distance
import ja3_converter as converter
import sys
import numpy as np
import matplotlib.pyplot as plt

data_path = "../data"

prod1 = sys.argv[1]
prod2 = sys.argv[2]
print("Drawing coordinates for {} and {} JA3s".format(prod1, prod2))

prod1_ja3 = converter.prod_to_ja3(prod1)
prod2_ja3 = converter.prod_to_ja3(prod2)

if prod1_ja3==None or prod2_ja3==None:
    print("Product does not exist in database.")
    prods = converter.all_prods()
    print("Available Products: {}".format(", ".join(prods)))
    exit()

ja3_distance.plot_scatter(prod1, prod2, prod1_ja3,prod2_ja3,1,3,"../graphs/{}_{}_ciph_goups.png".format(prod1,prod2))
ja3_distance.plot_scatter(prod1, prod2, prod1_ja3,prod2_ja3,1,2,"../graphs/{}_{}_ciph_extensions.png".format(prod1,prod2))

exit()

coordinates1 = ja3_distance.ja3s_to_coords(prod1_ja3)
coordinates2 = ja3_distance.ja3s_to_coords(prod2_ja3)

#print(str(coordinates1))
#print(str(coordinates2))

v,c,e,g,f = zip(*coordinates1)
v2,c2,e2,g2,f2 = zip(*coordinates2)

#plot ciph vs groups

fig = plt.figure()
plt.scatter(c,g,c="red",marker="o", label="{}".format(prod1))
#plt.scatter(x, y, c="red", alpha=0.5)
plt.scatter(c2, g2, c="blue", marker="x",label="{}".format(prod2))
plt.xlabel("Cipher suites")
plt.ylabel("Supported Groups")
plt.legend(bbox_to_anchor =(0.65, 1.15))
#plt.show()
fig.savefig("../graphs/{}_{}_ciph_goups.png".format(prod1,prod2))
plt.close(fig)


fig2 = plt.figure(2)
plt.scatter(c,e,c="red",marker="o", label="{}".format(prod1))
plt.scatter(c2, e2, c="blue", marker="x",label="{}".format(prod2))
plt.xlabel("Cipher suites")
plt.ylabel("Extensions")
plt.legend(bbox_to_anchor =(0.65, 1.15))
#plt.show()
fig2.savefig("../graphs/{}_{}_ciph_extensions.png".format(prod1,prod2))
plt.close(fig2)

import random

sw = (-23.612474, -46.702746)
ne = (-23.589548, -46.673392)


drivers = []

for i in range(1000):
    drivers.append((random.uniform(-23.613574, -23.589148), random.uniform(-46.703746, -46.652392)))
    # drivers.append((random.uniform(-23.612474, -23.589548), random.uniform(-46.702746, -46.673392)))


def is_inside_rectangle(sw, ne, point):
    if point[0] < sw[0] or point[0] > ne[0]:
        return False
    elif point[1] < sw[1] or point[1] > ne[1]:
        return False
    else:
        return True

inside = 0
outside = 0

for driver in drivers:
    if is_inside_rectangle(sw, ne, driver):
        inside = inside + 1
        print "++++++ {0}".format(driver)
    else:
        outside = outside + 1
        print "------ {0}".format(driver)

print "-------------------------------------------------"
print "---- inside: {0}".format(inside)
print "---- outside: {0}".format(outside)

sw = (-23.612474, -46.702746)
ne = (-23.589548, -46.673392)

driver1 = (-23.54981095, -46.69982655)
driver2 = (-23.60810717, -46.67500346)
driver3 = (-23.98287476, -46.11236872)

drivers = [driver1, driver2, driver3]

# sw = (0, 1)
# ne = (4, 5)
# point = (4, 5)


def is_inside_rectangle(sw, ne, point):
    if point[0] < sw[0] or point[0] > ne[0]:
        return False
    elif point[1] < sw[1] or point[1] > ne[1]:
        return False
    else:
        return True


for driver in drivers:
    print "--- {0}: {1}".format(driver, is_inside_rectangle(sw, ne, driver))

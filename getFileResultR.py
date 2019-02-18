for m in [2, 3]:
    model_name = "mngic" * (m == 1) + "mhdic" * (m == 2) + "mric" * (m == 3) + "mhadic" * (m == 4) + "mpmisic" * (m == 5) + "_pps"
    for pps in [1, 2, 3]:
        profit, cost, time_avg, time_total = [], [], [], []
        ratio_profit, ratio_cost, number_an, number_seed = [], [], [], []
        for data_setting in [2]:
            data_set_name = "email_directed" * (data_setting == 1) + "email_undirected" * (data_setting == 2) + \
                            "WikiVote_directed" * (data_setting == 3) + "NetPHY_undirected" * (data_setting == 4)
            for prod_setting in [1, 2]:
                for wpiwp in [bool(0), bool(1)]:
                    for prod_setting2 in [1, 2, 3]:
                        product_name = "r1p3n" + str(prod_setting) + "a" * (prod_setting2 == 2) + "b" * (prod_setting2 == 3)
                        path = "result/r/" + model_name + str(pps) + "_wpiwp" * wpiwp + "/" + \
                               model_name + str(pps) + "_wpiwp" * wpiwp + "_" + data_set_name + "_" + product_name

                        with open(path + "/profit.txt") as f:
                            for line in f:
                                profit.append(line)
                        f.close()
                        with open(path + "/cost.txt") as f:
                            for line in f:
                                cost.append(line)
                        f.close()
                        with open(path + "/time_avg.txt") as f:
                            for line in f:
                                time_avg.append(line)
                        f.close()
                        with open(path + "/time_total.txt") as f:
                            for line in f:
                                time_total.append(line)
                        f.close()

                for prod_setting2 in [1, 2, 3]:
                    product_name = "r1p3n" + str(prod_setting) + "a" * (prod_setting2 == 2) + "b" * (prod_setting2 == 3)
                    for wpiwp in [bool(0), bool(1)]:
                        path = "result/r/" + model_name + str(pps) + "_wpiwp" * wpiwp + "/" + \
                               model_name + str(pps) + "_wpiwp" * wpiwp + "_" + data_set_name + "_" + product_name

                        with open(path + "/ratio_profit.txt") as f:
                            for line in f:
                                ratio_profit.append(line)
                        f.close()
                        with open(path + "/ratio_cost.txt") as f:
                            for line in f:
                                ratio_cost.append(line)
                        f.close()
                        with open(path + "/number_an.txt") as f:
                            for line in f:
                                number_an.append(line)
                        f.close()
                        with open(path + "/number_seed.txt") as f:
                            for line in f:
                                number_seed.append(line)
                        f.close()

        pathw = "result/r/" + model_name + str(pps) + "_" + data_set_name
        fw = open(pathw + "_profit.txt", 'w')
        for lnum, line in enumerate(profit):
            fw.write(str(line) + "\n")
            if lnum == 5:
                fw.write("\n" * 10)
        fw.close()
        fw = open(pathw + "_cost.txt", 'w')
        for lnum, line in enumerate(cost):
            fw.write(str(line) + "\n")
            if lnum == 5:
                fw.write("\n" * 10)
        fw.close()
        fw = open(pathw + "_time_avg.txt", 'w')
        for lnum, line in enumerate(time_avg):
            fw.write(str(line) + "\n")
            if lnum == 5:
                fw.write("\n" * 10)
        fw.close()
        fw = open(pathw + "_time_total.txt", 'w')
        for lnum, line in enumerate(time_total):
            fw.write(str(line) + "\n")
            if lnum == 5:
                fw.write("\n" * 10)
        fw.close()

        fw = open(pathw + "_ratio_profit.txt", 'w')
        for lnum, line in enumerate(ratio_profit):
            if lnum % 6 == 0 and lnum != 0:
                fw.write("\n" * 9)
            fw.write(str(line))
        fw.close()
        fw = open(pathw + "_ratio_cost.txt", 'w')
        for lnum, line in enumerate(ratio_cost):
            if lnum % 6 == 0 and lnum != 0:
                fw.write("\n" * 9)
            fw.write(str(line))
        fw.close()
        fw = open(pathw + "_number_an.txt", 'w')
        for lnum, line in enumerate(number_an):
            if lnum % 6 == 0 and lnum != 0:
                fw.write("\n" * 9)
            fw.write(str(line))
        fw.close()
        fw = open(pathw + "_number_seed.txt", 'w')
        for lnum, line in enumerate(number_seed):
            if lnum % 6 == 0 and lnum != 0:
                fw.write("\n" * 9)
            fw.write(str(line))
        fw.close()

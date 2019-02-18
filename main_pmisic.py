from SeedSelection_PMIS import *

if __name__ == "__main__":
    for pps in [1, 2, 3]:
        for wpiwp in [bool(0), bool(1)]:
            for data_setting in [2]:
                data_set_name = "email_directed" * (data_setting == 1) + "email_undirected" * (data_setting == 2) + \
                                "WikiVote_directed" * (data_setting == 3) + "NetPHY_undirected" * (data_setting == 4)
                for prod_setting in [1, 2]:
                    for prod_setting2 in [1, 2, 3]:
                        product_name = "r1p3n" + str(prod_setting) + "a" * (prod_setting2 == 2) + "b" * (prod_setting2 == 3)

                        total_budget = 3
                        sample_number, sample_output_number = 2, 2

                        iniG = IniGraph(data_set_name)
                        iniP = IniProduct(product_name)

                        seed_cost_dict = iniG.constructSeedCostDict()[1]
                        graph_dict = iniG.constructGraphDict()
                        product_list = iniP.getProductList()[0]
                        wallet_list = iniG.getWalletList(product_name)
                        num_node = len(seed_cost_dict)
                        num_product = len(product_list)

                        for bud in range(1, total_budget + 1):
                            start_time = time.time()

                            sspmis_main = SeedSelectionPMIS(graph_dict, seed_cost_dict, product_list, bud, pps, wpiwp)
                            dnic_main = DiffusionNormalIC(graph_dict, seed_cost_dict, product_list, pps, wpiwp)
                            eva_main = Evaluation(graph_dict, seed_cost_dict, product_list, pps, wpiwp)

                            personal_prob_list = dnic_main.setPersonalProbList(wallet_list)

                            result = []
                            avg_profit, avg_budget = 0.0, 0.0
                            avg_num_k_seed, avg_num_k_pn = [0 for _ in range(num_product)], [0 for _ in range(num_product)]
                            profit_k_list, budget_k_list = [0.0 for _ in range(num_product)], [0.0 for _ in range(num_product)]

                            s_matrix, p_matrix, c_matrix = sspmis_main.generateDecomposedResult(copy.deepcopy(wallet_list), copy.deepcopy(personal_prob_list))

                            for sample_count in range(sample_number):
                                print("pp_strategy = " + str(pps) + ", wpiwp = " + str(wpiwp) + ", data_set_name = " + data_set_name +
                                      ", product_name = " + product_name + ", budget = " + str(bud) + ", sample_count = " + str(sample_count))
                                now_budget = 0.0
                                seed_set = [set() for _ in range(num_product)]
                                mep_result = [0.0, 0.0, [0 for _ in range(num_product)], [0.0 for _ in range(num_product)], [set() for _ in range(num_product)]]

                                bud_index = [0 for _ in range(num_product)]
                                bud_upper_index = [len(kk) - 1 for kk in copy.deepcopy(c_matrix)]

                                while not operator.eq(bud_index, bud_upper_index):
                                    bud_pmis = 0
                                    for kk in range(num_product):
                                        bud_pmis += copy.deepcopy(c_matrix)[kk][bud_index[kk]]

                                    if bud_pmis <= bud:
                                        seed_set = [set() for _ in range(num_product)]
                                        for kk in range(num_product):
                                            seed_set[kk] = copy.deepcopy(s_matrix)[kk][bud_index[kk]][kk]

                                        pro_acc, pro_k_list_acc, pnn_k_list_acc = 0.0, [0.0 for _ in range(num_product)], [0 for _ in range(num_product)]
                                        for _ in range(100):
                                            pro, pro_k_list, pnn_k_list = eva_main.getSeedSetProfit(seed_set, copy.deepcopy(wallet_list), copy.deepcopy(personal_prob_list))
                                            pro_acc += pro
                                            for kk in range(num_product):
                                                pro_k_list_acc[kk] += pro_k_list[kk]
                                                pnn_k_list_acc[kk] += pnn_k_list[kk]
                                        pro_acc = round(pro_acc / 100, 2)
                                        for kk in range(num_product):
                                            profit_k_list[kk] += round(pro_k_list_acc[kk] / 100, 2)
                                            pnn_k_list_acc[kk] = round(pnn_k_list_acc[kk] / 100, 2)

                                        if pro_acc > mep_result[0]:
                                            mep_result = [pro_acc, bud_pmis, [len(kk) for kk in seed_set], pnn_k_list_acc, seed_set]

                                    pointer = num_product - 1
                                    while bud_index[pointer] == bud_upper_index[pointer]:
                                        bud_index[pointer] = 0
                                        pointer -= 1
                                    bud_index[pointer] += 1

                                now_profit = mep_result[0]
                                for kk in range(num_product):
                                    for ii in mep_result[4][kk]:
                                        now_budget += seed_cost_dict[ii]
                                        budget_k_list[kk] += seed_cost_dict[ii]

                                # -- result --
                                result.append(mep_result)
                                avg_profit += now_profit
                                avg_budget += now_budget
                                for kk in range(num_product):
                                    profit_k_list[kk] = round(profit_k_list[kk], 2)
                                    budget_k_list[kk] = round(budget_k_list[kk], 2)
                                    avg_num_k_seed[kk] += mep_result[2][kk]
                                    avg_num_k_pn[kk] += mep_result[3][kk]

                                # -- result --
                                how_long = round(time.time() - start_time, 2)
                                print("total_time: " + str(how_long) + "sec")
                                print(result[sample_count])
                                print("avg_profit = " + str(round(avg_profit / (sample_count + 1), 4)) + ", avg_budget = " + str(round(avg_budget / (sample_count + 1), 4)))
                                print("------------------------------------------")

                                if (sample_count + 1) % sample_output_number == 0:
                                    path1 = "result/mpmisic_pps" + str(pps) + "_wpiwp" * wpiwp
                                    if not os.path.isdir(path1):
                                        os.mkdir(path1)
                                    path = "result/mpmisic_pps" + str(pps) + "_wpiwp" * wpiwp + "/" +\
                                           data_set_name + "_" + product_name
                                    if not os.path.isdir(path):
                                        os.mkdir(path)
                                    fw = open(path + "/" + "b" + str(bud) + "_i" + str(sample_count + 1) + ".txt", 'w')
                                    fw.write("mpmisic, pp_strategy = " + str(pps) + ", total_budget = " + str(bud) + ", wpiwp = " + str(wpiwp) + "\n" +
                                             "data_set_name = " + data_set_name + ", product_name = " + product_name + "\n" +
                                             "total_budget = " + str(bud) + ", sample_count = " + str(sample_count + 1) + "\n" +
                                             "avg_profit = " + str(round(avg_profit / (sample_count + 1), 4)) +
                                             ", avg_budget = " + str(round(avg_budget / (sample_count + 1), 4)) + "\n" +
                                             "total_time = " + str(how_long) + ", avg_time = " + str(round(how_long / (sample_count + 1), 4)) + "\n")
                                    fw.write("\nprofit_ratio =")
                                    for kk in range(num_product):
                                        fw.write(" " + str(round(profit_k_list[kk] / (sample_count + 1), 4)))
                                    fw.write("\nbudget_ratio =")
                                    for kk in range(num_product):
                                        fw.write(" " + str(round(budget_k_list[kk] / (sample_count + 1), 4)))
                                    fw.write("\nseed_number =")
                                    for kk in range(num_product):
                                        fw.write(" " + str(round(avg_num_k_seed[kk] / (sample_count + 1), 4)))
                                    fw.write("\ncustomer_number =")
                                    for kk in range(num_product):
                                        fw.write(" " + str(round(avg_num_k_pn[kk] / (sample_count + 1), 4)))
                                    fw.write("\n")

                                    for t, r in enumerate(result):
                                        fw.write("\n" + str(t) + " " + str(round(r[0], 4)) + " " + str(round(r[1], 4)) + " " + str(r[2]) + " " + str(r[3]) + " " + str(r[4]))
                                    fw.close()
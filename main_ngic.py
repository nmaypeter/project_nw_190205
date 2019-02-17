from SeedSelection_NaiveGreedy import *

if __name__ == "__main__":
    for pps in [1, 2, 3]:
        for wpiwp in [bool(0), bool(1)]:
            for data_setting in [2]:
                data_set_name = "email_directed" * (data_setting == 1) + "email_undirected" * (data_setting == 2) + \
                                "WikiVote_directed" * (data_setting == 3) + "NetPHY_undirected" * (data_setting == 4)
                for prod_setting in [1, 2]:
                    for prod_setting2 in [1, 2, 3]:
                        product_name = "r1p3n" + str(prod_setting) + "a" * (prod_setting2 == 2) + "b" * (prod_setting2 == 3)

                        total_budget = 10
                        sample_number, sample_output_number = 10, 10

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

                            ssng_main = SeedSelectionNG(graph_dict, seed_cost_dict, product_list, bud, pps, wpiwp)
                            dnic_main = DiffusionNormalIC(graph_dict, seed_cost_dict, product_list, pps, wpiwp)
                            eva_main = Evaluation(graph_dict, seed_cost_dict, product_list, pps, wpiwp)

                            personal_prob_list = dnic_main.setPersonalProbList(wallet_list)

                            result = []
                            avg_profit, avg_budget = 0.0, 0.0
                            avg_num_k_seed, avg_num_k_pn = [0 for _ in range(num_product)], [0 for _ in range(num_product)]
                            profit_k_list, budget_k_list = [0.0 for _ in range(num_product)], [0.0 for _ in range(num_product)]

                            for sample_count in range(sample_number):
                                print("pp_strategy = " + str(pps) + ", wpiwp = " + str(wpiwp) + ", data_set_name = " + data_set_name +
                                      ", product_name = " + product_name + ", budget = " + str(bud) + ", sample_count = " + str(sample_count))
                                now_profit, now_budget = 0.0, 0.0
                                seed_set = [set() for _ in range(num_product)]
                                notban_seed_set = [set(graph_dict.keys()) for _ in range(num_product)]

                                mep_g, nban_seed_set = ssng_main.getMostValuableSeed(seed_set, copy.deepcopy(notban_seed_set), now_budget, copy.deepcopy(wallet_list), copy.deepcopy(personal_prob_list))
                                mep_k_prod, mep_i_node, mep_profit = mep_g[0], mep_g[1], mep_g[2]

                                # -- main --
                                while now_profit < mep_profit and mep_i_node != '-1':
                                    for kk in range(num_product):
                                        if mep_i_node in nban_seed_set[kk]:
                                            nban_seed_set[kk].remove(mep_i_node)
                                    seed_set[mep_k_prod].add(mep_i_node)

                                    budget_k_list[mep_k_prod] += seed_cost_dict[mep_i_node]
                                    now_profit = mep_profit
                                    now_budget += seed_cost_dict[mep_i_node]

                                    mep_g, nban_seed_set = ssng_main.getMostValuableSeed(seed_set, nban_seed_set, now_budget, copy.deepcopy(wallet_list), copy.deepcopy(personal_prob_list))
                                    mep_k_prod, mep_i_node, mep_profit = mep_g[0], mep_g[1], mep_g[2]

                                # -- sample result --
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
                                now_budget = round(now_budget, 2)

                                # -- result --
                                now_num_k_seed = [len(kk) for kk in seed_set]
                                result.append([pro_acc, now_budget, now_num_k_seed, pnn_k_list_acc, seed_set])
                                avg_profit += now_profit
                                avg_budget += now_budget
                                for kk in range(num_product):
                                    budget_k_list[kk] = round(budget_k_list[kk], 2)
                                    avg_num_k_seed[kk] += now_num_k_seed[kk]
                                    avg_num_k_pn[kk] += pnn_k_list_acc[kk]

                                # -- result --
                                how_long = round(time.time() - start_time, 2)
                                print("total_time: " + str(how_long) + "sec")
                                print(result[sample_count])
                                print("avg_profit = " + str(round(avg_profit / (sample_count + 1), 4)) + ", avg_budget = " + str(round(avg_budget / (sample_count + 1), 4)))
                                print("------------------------------------------")

                                if (sample_count + 1) % sample_output_number == 0:
                                    path1 = "result/mngic_pps" + str(pps) + "_wpiwp" * wpiwp
                                    if not os.path.isdir(path1):
                                        os.mkdir(path1)
                                    path = "result/mngic_pps" + str(pps) + "_wpiwp" * wpiwp + "/" +\
                                           data_set_name + "_" + product_name
                                    if not os.path.isdir(path):
                                        os.mkdir(path)
                                    fw = open(path + "/" + "b" + str(bud) + "_i" + str(sample_count + 1) + ".txt", 'w')
                                    fw.write("mngic, pp_strategy = " + str(pps) + ", total_budget = " + str(bud) + ", wpiwp = " + str(wpiwp) + "\n" +
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

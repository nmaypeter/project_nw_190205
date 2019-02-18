from Diffusion_NormalIC import *


class generateNTL:
    def __init__(self, g_dict, s_c_dict, prod_list, total_bud, pps, wpiwp):
        ### g_dict: (dict) the graph
        ### s_c_dict: (dict) the set of cost for seeds
        ### prod_list: (list) the set to record products [kk's profit, kk's cost, kk's price]
        ### total_bud: (int) the budget to select seed
        ### num_node: (int) the number of nodes
        ### num_product: (int) the kinds of products
        ### pps: (int) the strategy to update personal prob.
        ### wpiwp: (bool) whether passing the information without purchasing
        self.graph_dict = g_dict
        self.seed_cost_dict = s_c_dict
        self.product_list = prod_list
        self.total_budget = total_bud
        self.num_node = len(s_c_dict)
        self.num_product = len(prod_list)
        self.pps = pps
        self.wpiwp = wpiwp

    def updateExpectProfitList(self, s_set, w_list, pp_list, t_list):
        # -- calculate expected profit for all combinations of nodes and products --
        dnic_g = DiffusionNormalIC(self.graph_dict, self.seed_cost_dict, self.product_list, self.pps, self.wpiwp)

        for k in range(self.num_product):
            for i in range(self.num_node):
                print(k, i)
                ep = dnic_g.getSeedSetProfit(k, str(i), s_set, copy.deepcopy(w_list), copy.deepcopy(pp_list))[0]
                t_list[k * self.num_node + i].append(ep)
                t_list[k * self.num_node + i].append(0)

        return t_list


if __name__ == "__main__":
    data_set_name = "email_undirected"
    product_name = "r1p3n1"
    total_budget = 8
    pp_strategy = 1
    whether_passing_information_without_purchasing = bool(0)

    iniG = IniGraph(data_set_name)
    iniP = IniProduct(product_name)

    seed_cost_dict = iniG.constructSeedCostDict()[1]
    graph_dict = iniG.constructGraphDict()
    product_list = iniP.getProductList()[0]
    wallet_list = iniG.getWalletList(product_name)
    num_node = len(seed_cost_dict)
    num_product = len(product_list)

    # -- initialization for each budget --
    start_time = time.time()

    gntl = generateNTL(graph_dict, seed_cost_dict, product_list, total_budget, pp_strategy, whether_passing_information_without_purchasing)
    dnic = DiffusionNormalIC(graph_dict, seed_cost_dict, product_list, pp_strategy, whether_passing_information_without_purchasing)
    eva = Evaluation(graph_dict, seed_cost_dict, product_list, pp_strategy, whether_passing_information_without_purchasing)

    personal_prob_list = dnic.setPersonalProbList(wallet_list)

    ### result: (list) [profit, budget, seed number per product, customer number per product, seed set] in this execution_time
    result = []
    avg_profit, avg_budget = 0.0, 0.0
    avg_num_k_seed, avg_num_k_pn = [0 for _ in range(num_product)], [0 for _ in range(num_product)]
    profit_k_list, budget_k_list = [0.0 for _ in range(num_product)], [0.0 for _ in range(num_product)]

    # -- initialization for each sample_number --
    ### now_profit, now_budget: (float) the profit and budget in this execution_time
    now_profit, now_budget = 0.0, 0.0
    ### seed_set: (list) the seed set
    ### seed_set[kk]: (set) the seed set for kk-product
    seed_set = [set() for _ in range(num_product)]

    total_list = [[] for _ in range(num_node * num_product)]

    for kk in range(num_product):
        for ii in range(num_node):
            total_list[kk * num_node + ii].append(kk)
            total_list[kk * num_node + ii].append(ii)
            total_list[kk * num_node + ii].append(iniG.getNodeOutDegree(str(ii)))
            total_list[kk * num_node + ii].append(0)

            affordable_deg = 0
            if str(ii) in graph_dict:
                for ad in graph_dict[str(ii)]:
                    if wallet_list[int(ad)] >= product_list[kk][2]:
                        affordable_deg += 1
            total_list[kk * num_node + ii].append(affordable_deg)
            total_list[kk * num_node + ii].append(0)
    exp_profit_list = gntl.updateExpectProfitList([set() for _ in range(num_product)], copy.deepcopy(wallet_list), copy.deepcopy(personal_prob_list), total_list)

    llist, llist2, llist3 = [], [], []
    for item in total_list:
        if item[2] in llist:
            continue
        else:
            llist.append(item[2])
    for item in total_list:
        if item[4] in llist2:
            continue
        else:
            llist2.append(item[4])
    for item in total_list:
        if item[6] in llist3:
            continue
        else:
            llist3.append(item[6])
    llist = sorted(llist, reverse=True)
    llist2 = sorted(llist2, reverse=True)
    llist3 = sorted(llist3, reverse=True)
    print(len(llist), len(llist2), len(llist3))

    for item in total_list:
        for ll in llist:
            if item[2] == ll:
                item[3] = llist.index(ll) + 1
        for ll in llist2:
            if item[4] == ll:
                item[5] = llist2.index(ll) + 1
        for ll in llist3:
            if item[6] == ll:
                item[7] = llist3.index(ll) + 1

    fw = open("total_list.txt", 'w')
    for item in total_list:
        item_kk_ii = ""
        t = 0
        for kk_ii in item:
            t += 1
            item_kk_ii += str(kk_ii) + "\t"
            if t % 2 == 0:
                item_kk_ii += "\t"
        fw.write(item_kk_ii + "\n")
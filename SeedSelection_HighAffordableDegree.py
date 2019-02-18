from Diffusion_NormalIC import *


class SeedSelectionHAD:
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

    def constructAffordableDegreeDict(self, s_set, w_list):
        union_s_set = set()
        for k in range(len(s_set)):
            union_s_set = union_s_set | s_set[k]

        d_dict = [{} for _ in range(self.num_product)]
        for k in range(self.num_product):
            for i in range(self.num_node):
                if str(i) in union_s_set:
                    continue
                count_affordable_node = 0
                if str(i) in self.graph_dict:
                    for ad in self.graph_dict[str(i)]:
                        if w_list[int(ad)] >= self.product_list[k][2]:
                            count_affordable_node += 1

                if count_affordable_node in d_dict[k]:
                    d_dict[k][str(count_affordable_node)].add(str(i))
                else:
                    d_dict[k][str(count_affordable_node)] = {str(i)}

        return d_dict

    def getHighDegreeNode(self, d_dict, cur_bud):
        # -- get the node with highest degree --
        mep = [0, '-1']
        max_degree = [-1 for _ in range(self.num_product)]
        while mep[1] == '-1':
            for k in range(self.num_product):
                while max_degree[k] == -1:
                    for deg in list(d_dict[k].keys()):
                        if int(deg) > max_degree[k]:
                            max_degree[k] = int(deg)

                    if max_degree[k] == -1:
                        break

                    if d_dict[k][str(max_degree[k])] == set():
                        del d_dict[k][str(max_degree[k])]
                        max_degree[k] = -1

                if max_degree[k] == -1:
                    continue

                if d_dict[k][str(max_degree[k])] == set():
                    del d_dict[k][str(max_degree[k])]
                    max_degree[k] = -1

            mep[0] = max_degree.index(max(max_degree))
            if max_degree[mep[0]] == -1:
                return mep, d_dict
            mep[1] = choice(list(d_dict[mep[0]][str(max_degree[mep[0]])]))
            d_dict[mep[0]][str(max_degree[mep[0]])].remove(mep[1])

            if self.seed_cost_dict[mep[1]] + cur_bud > self.total_budget:
                mep[1] = '-1'

        return mep, d_dict


if __name__ == "__main__":
    data_set_name = "email_undirected"
    product_name = "r1p3n1"
    total_budget = 10
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

    sshad = SeedSelectionHAD(graph_dict, seed_cost_dict, product_list, total_budget, pp_strategy, whether_passing_information_without_purchasing)
    dnic = DiffusionNormalIC(graph_dict, seed_cost_dict, product_list, pp_strategy, whether_passing_information_without_purchasing)
    eva = Evaluation(graph_dict, seed_cost_dict, product_list, pp_strategy, whether_passing_information_without_purchasing)

    personal_prob_list = dnic.setPersonalProbList(wallet_list)

    ### result: (list) [profit, budget, seed number per product, customer number per product, seed set] in this execution_time
    result = []
    avg_profit, avg_budget = 0.0, 0.0
    avg_num_k_seed, avg_num_k_pn = [0 for _ in range(num_product)], [0 for _ in range(num_product)]
    profit_k_list, budget_k_list = [0.0 for _ in range(num_product)], [0.0 for _ in range(num_product)]

    # -- initialization for each sample_number --
    ### now_budget: (float) the budget in this execution_time
    now_budget = 0.0
    ### seed_set: (list) the seed set
    ### seed_set[kk]: (set) the seed set for kk-product
    seed_set = [set() for _ in range(num_product)]

    degree_dict = sshad.constructAffordableDegreeDict(seed_set, copy.deepcopy(wallet_list))
    mep_g, degree_dict = sshad.getHighDegreeNode(degree_dict, now_budget)
    mep_k_prod, mep_i_node = mep_g[0], mep_g[1]

    # -- main --
    while now_budget < total_budget and mep_i_node != '-1':
        seed_set[mep_k_prod].add(mep_i_node)

        budget_k_list[mep_k_prod] += seed_cost_dict[mep_i_node]
        now_budget += seed_cost_dict[mep_i_node]

        mep_g, degree_dict = sshad.getHighDegreeNode(degree_dict, now_budget)
        mep_k_prod, mep_i_node = mep_g[0], mep_g[1]

    pro_acc, pro_k_list_acc, pnn_k_list_acc = 0.0, [0.0 for _ in range(num_product)], [0 for _ in range(num_product)]
    for _ in range(100):
        pro, pro_k_list, pnn_k_list = eva.getSeedSetProfit(seed_set, copy.deepcopy(wallet_list), copy.deepcopy(personal_prob_list))
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
    avg_profit += pro_acc
    avg_budget += now_budget
    for kk in range(num_product):
        budget_k_list[kk] = round(budget_k_list[kk], 2)
        avg_num_k_seed[kk] += now_num_k_seed[kk]
        avg_num_k_pn[kk] += pnn_k_list_acc[kk]
    how_long = round(time.time() - start_time, 2)
    print("result")
    print(result)
    print("\npro_k_list, budget_k_list")
    print(profit_k_list, budget_k_list)
    print("total time: " + str(how_long) + "sec")
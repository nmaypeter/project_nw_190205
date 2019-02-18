from Diffusion_NormalIC import *
import operator


class SeedSelectionPMIS:
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

    def getMostValuableSeed(self, k_prod, s_set, nban_set, cur_bud, w_list, pp_list):
        # -- calculate expected profit for all combinations of nodes and products --
        ### ban_set: (list) the set to record the node that will be banned
        ### mep: (list) [#product, #node, expected profit]
        ban_set = set()
        mep = [k_prod, '-1', 0.0]
        m_diff_times = 0

        dnic_s = DiffusionNormalIC(self.graph_dict, self.seed_cost_dict, self.product_list, self.pps, self.wpiwp)

        for i in nban_set:
            # -- the cost of seed cannot exceed the budget --
            if self.seed_cost_dict[i] + cur_bud > self.total_budget:
                ban_set.add(i)
                continue
            ep, diff_times = dnic_s.getSeedSetProfit(k_prod, i, s_set, copy.deepcopy(w_list), copy.deepcopy(pp_list))
            m_diff_times = max(m_diff_times, diff_times)

            # -- the expected profit cannot be negative --
            if ep <= 0:
                ban_set.add(i)
                continue

            # -- the diffusion times cannot be too low --
            if diff_times <= m_diff_times * 0.1:
                ban_set.add(i)
                continue

            # -- choose the better seed --
            if ep > mep[2]:
                mep = [k_prod, i, ep]

        # -- remove the impossible seeds from nban_set
        for k in range(self.num_product):
            for i in ban_set:
                if i in nban_set:
                    nban_set.remove(i)

        return mep, nban_set

    def generateDecomposedResult(self, w_list, pp_list):
        start_time = time.time()
        s_matrix, p_matrix, c_matrix = [[] for _ in range(self.num_product)], [[] for _ in range(self.num_product)], [[] for _ in range(self.num_product)]
        sspmis_ss = SeedSelectionPMIS(self.graph_dict, self.seed_cost_dict, self.product_list, self.total_budget, self.pps, self.wpiwp)

        for k in range(self.num_product):
            s_matrix[k].append([set() for _ in range(self.num_product)])
            p_matrix[k].append(0.0)
            c_matrix[k].append(0.0)

            seed_set_t = [set() for _ in range(self.num_product)]
            nban_set_k = {i for i in self.graph_dict}
            cur_profit, cur_budget = 0.0, 0.0

            mep, nban_seed_set = sspmis_ss.getMostValuableSeed(k, seed_set_t, copy.deepcopy(nban_set_k), cur_budget, copy.deepcopy(w_list), copy.deepcopy(pp_list))
            mep_k_prod, mep_i_node, mep_profit = mep[0], mep[1], mep[2]
            print(round(time.time() - start_time, 2))
            temp_time = time.time()

            while cur_profit < mep_profit:
                if mep_i_node in nban_set_k:
                    nban_set_k.remove(mep_i_node)
                seed_set_t[mep_k_prod].add(mep_i_node)

                cur_profit = mep_profit
                cur_budget += self.seed_cost_dict[mep_i_node]
                s_matrix[k].append(copy.deepcopy(seed_set_t))
                p_matrix[k].append(cur_profit)
                c_matrix[k].append(round(cur_budget, 2))
                print(mep, round(cur_budget, 2))

                mep, nban_seed_set = sspmis_ss.getMostValuableSeed(k, seed_set_t, nban_seed_set, cur_budget, copy.deepcopy(w_list), copy.deepcopy(pp_list))
                mep_k_prod, mep_i_node, mep_profit = mep[0], mep[1], mep[2]
                print(round(time.time() - temp_time, 2))
                print(round(time.time() - start_time, 2))
                temp_time = time.time()

        return s_matrix, p_matrix, c_matrix


if __name__ == "__main__":
    data_set_name = "email_undirected"
    product_name = "r1p3n1"
    total_budget = 2
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

    sspmis = SeedSelectionPMIS(graph_dict, seed_cost_dict, product_list, total_budget, pp_strategy, whether_passing_information_without_purchasing)
    dnic = DiffusionNormalIC(graph_dict, seed_cost_dict, product_list, pp_strategy, whether_passing_information_without_purchasing)
    eva = Evaluation(graph_dict, seed_cost_dict, product_list, pp_strategy, whether_passing_information_without_purchasing)

    personal_prob_list = dnic.setPersonalProbList(wallet_list)

    ### result: (list) [profit, budget, seed number per product, customer number per product, seed set] in this execution_time
    result = []
    avg_profit, avg_budget = 0.0, 0.0
    avg_num_k_seed, avg_num_k_pn = [0 for _ in range(num_product)], [0 for _ in range(num_product)]
    profit_k_list, budget_k_list = [0.0 for _ in range(num_product)], [0.0 for _ in range(num_product)]

    s_matrix, p_matrix, c_matrix = sspmis.generateDecomposedResult(copy.deepcopy(wallet_list), copy.deepcopy(personal_prob_list))

    # -- initialization for each sample_number --
    ### now_profit, now_budget: (float) the profit and budget in this execution_time
    now_profit, now_budget = 0.0, 0.0
    ### seed_set: (list) the seed set
    ### seed_set[kk]: (set) the seed set for kk-product
    seed_set = [set() for _ in range(num_product)]
    mep_result = [0.0, 0.0, [0 for _ in range(num_product)], [0.0 for _ in range(num_product)], [set() for _ in range(num_product)]]

    bud_index = [0 for _ in range(num_product)]
    bud_upper_index = [len(kk) - 1 for kk in c_matrix]

    while not operator.eq(bud_index, bud_upper_index):
        bud_pmis = 0
        for kk in range(num_product):
            bud_pmis += c_matrix[kk][bud_index[kk]]

        if bud_pmis <= total_budget:
            seed_set = [set() for _ in range(num_product)]
            for kk in range(num_product):
                seed_set[kk] = s_matrix[kk][bud_index[kk]][kk]

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
    how_long = round(time.time() - start_time, 2)
    print("result")
    print(result)
    print("\npro_k_list, budget_k_list")
    print(profit_k_list, budget_k_list)
    print("total time: " + str(how_long) + "sec")

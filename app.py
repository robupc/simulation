import time
import streamlit as st
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field

# ---------------------------
# 　元ファイルのロジック（基本部分）　
# ---------------------------
@dataclass
class Node:
    name: str                    # 会員の名前（例："Node_1"）
    position_number: int         # ポジション数（例: 1, 3, 5, 7）
    bank_number: int = 0         # バンク保有数
    active: bool = True          # アクティブ状態
    parent_node: Optional[str] = None   # 親ノードの名前
    tree_number: int = 0         # 自分を含むツリー内の総人数
    title_rank: int = 0          # 現在のタイトルランク
    past_title_rank: int = 0     # 1シーズン前のタイトルランク
    paid_point: int = 0          # 売上（支払額）
    bonus_point: int = 0         # そのシーズンに発生したボーナス
    total_paid_point: int = 0    # 売上合計
    total_bonus_point: int = 0   # ボーナス合計
    children: List['Node'] = field(default_factory=list)  # 直接下の会員リスト
    # バイナリーサイズ（それぞれのポジション用）
    binary_number_1: int = 0     
    binary_number_3: int = 0     
    binary_number_5: int = 0     
    binary_number_7: int = 0     

    def process_bank_number(self, node1: 'Node', node2: 'Node') -> None:
        if not node1 or not node2:
            return
        tree1 = node1.tree_number
        tree2 = node2.tree_number
        if tree1 != tree2:
            while self.bank_number > 0 and tree2 < tree1:
                tree2 += 1
                self.bank_number -= 1
            diff = min(tree1 - tree2, 2)
            if diff > 0:
                self.bank_number = min(self.bank_number + diff, 2)

    def calculate_binary_numbers(self) -> None:
        active_children = sorted(
            [child for child in self.children if child.active],
            key=lambda x: x.tree_number,
            reverse=True
        )
        if not active_children:
            return

        if self.position_number >= 1 and len(active_children) >= 2:
            node1, node2 = active_children[0:2]
            self.binary_number_1 = (min(node1.tree_number, node2.tree_number) - 1) * 2
            self.process_bank_number(node1, node2)

        if self.position_number >= 3 and len(active_children) >= 4:
            node3, node4 = active_children[2:4]
            self.binary_number_3 = (min(node3.tree_number, node4.tree_number) - 1) * 2
            self.process_bank_number(node3, node4)

        if self.position_number >= 5 and len(active_children) >= 6:
            node5, node6 = active_children[4:6]
            self.binary_number_5 = (min(node5.tree_number, node6.tree_number) - 1) * 2
            self.process_bank_number(node5, node6)

        if self.position_number >= 7 and len(active_children) >= 8:
            node7, node8 = active_children[6:8]
            self.binary_number_7 = (min(node7.tree_number, node8.tree_number) - 1) * 2
            self.process_bank_number(node7, node8)

    def activate(self) -> None:
        self.paid_point += 20790
        self.total_paid_point += 20790
        self.active = True

    def set_position(self, position: int) -> None:
        # ※ 実際の計算用であれば外部入力により費用設定も変更可能
        position_costs = {1: 41580, 3: 82060, 5: 122540, 7: 163020}
        if position in position_costs:
            self.position_number = position
            self.paid_point += position_costs[position]
            self.total_paid_point += position_costs[position]

    def calculate_tree_number(self) -> int:
        count = 1
        for child in self.children:
            if child.active:
                count += child.calculate_tree_number()
        return count

    def update_title_rank(self) -> None:
        tree_size = self.calculate_tree_number()
        active_children = len([child for child in self.children if child.active])
        # タイトルランクの条件（これも入力可能に変更可能）
        rank_conditions = [
            (20, 2, 1), (60, 3, 2), (200, 4, 3),
            (600, 5, 4), (1000, 7, 5), (2000, 10, 6),
            (4000, 10, 7), (6000, 10, 8), (10000, 10, 9),
            (20000, 10, 10)
        ]
        self.past_title_rank = self.title_rank
        self.title_rank = 0
        for tree_req, children_req, rank in rank_conditions:
            if tree_size >= tree_req and active_children >= children_req:
                self.title_rank = rank

    def calculate_riseup_binary_bonus(self, bonus_params: Dict[str, float]) -> int:
        def calculate_bonus_for_binary(binary_number: int) -> float:
            # 各段階の定数は bonus_params から取得する
            if 4 <= binary_number <= 60:
                return bonus_params["level1"] * binary_number / 4
            elif 64 <= binary_number <= 200:
                return bonus_params["level1"] * 15 + bonus_params["level2"] * (binary_number - 60) / 4
            elif 204 <= binary_number <= 2000:
                return bonus_params["level1"] * 15 + bonus_params["level2"] * 35 + bonus_params["level3"] * (binary_number - 200) / 4
            elif 2004 <= binary_number <= 20000:
                return bonus_params["level1"] * 15 + bonus_params["level2"] * 35 + bonus_params["level3"] * 450 + bonus_params["level4"] * (binary_number - 2000) / 4
            elif binary_number > 20000:
                return bonus_params["level1"] * 15 + bonus_params["level2"] * 35 + bonus_params["level3"] * 450 + bonus_params["level4"] * 4500
            return 0
        bonus = 0
        if self.position_number >= 1:
            bonus += calculate_bonus_for_binary(self.binary_number_1)
        if self.position_number >= 3:
            bonus += calculate_bonus_for_binary(self.binary_number_3)
        if self.position_number >= 5:
            bonus += calculate_bonus_for_binary(self.binary_number_5)
        if self.position_number >= 7:
            bonus += calculate_bonus_for_binary(self.binary_number_7)
        return int(bonus)

    def calculate_product_free_bonus(self, bonus_pf: Dict[str, int]) -> int:
        def calculate_bonus_for_binary(binary_number: int) -> int:
            if binary_number == 4:
                return bonus_pf["pf4"]
            elif binary_number == 8:
                return bonus_pf["pf8"]
            elif binary_number == 12:
                return bonus_pf["pf12"]
            elif binary_number == 16:
                return bonus_pf["pf16"]
            return 0

        bonus = 0
        if self.position_number >= 1:
            bonus += calculate_bonus_for_binary(self.binary_number_1)
        if self.position_number >= 3:
            bonus += calculate_bonus_for_binary(self.binary_number_3)
        if self.position_number >= 5:
            bonus += calculate_bonus_for_binary(self.binary_number_5)
        if self.position_number >= 7:
            bonus += calculate_bonus_for_binary(self.binary_number_7)
        return bonus

    def calculate_matching_bonus(self, bonus_pf: Dict[str, int], total_paid_points: int) -> int:
        bonus = 0
        for child in self.children:
            if child.active:
                bonus += child.calculate_riseup_binary_bonus(bonus_pf) * 0.15
                for grandchild in child.children:
                    if grandchild.active:
                        bonus += grandchild.calculate_riseup_binary_bonus(bonus_pf) * 0.05
                        for great_grandchild in grandchild.children:
                            if great_grandchild.active:
                                bonus += great_grandchild.calculate_riseup_binary_bonus(bonus_pf) * 0.05
        return int(bonus)

    def calculate_car_bonus(self) -> int:
        if self.title_rank >= 4 and self.past_title_rank >= 4:
            return 100000
        return 0

    def calculate_house_bonus(self) -> int:
        if self.title_rank >= 5 and self.past_title_rank >= 5:
            return 150000
        return 0

    def calculate_sharing_bonus(self, total_paid_points: int) -> int:
        if self.title_rank == 3:
            return int(total_paid_points * 0.01)
        elif self.title_rank >= 4:
            return int(total_paid_points * 0.002)
        return 0

    def arrange_tree(self) -> None:
        if not self.active:
            return
        active_children = [child for child in self.children if child.active]
        active_children.sort(key=lambda x: x.calculate_tree_number(), reverse=True)
        if self.position_number == 1:
            self._arrange_position1(active_children)
        elif self.position_number == 3:
            self._arrange_position3(active_children)
        elif self.position_number == 5:
            self._arrange_position5(active_children)
        elif self.position_number == 7:
            self._arrange_position7(active_children)

    def _arrange_position1(self, children: List['Node']) -> None:
        if len(children) < 2:
            return
        columns = [children[0:1], children[1:2]]
        self._balance_columns(columns)

    def _arrange_position3(self, children: List['Node']) -> None:
        if len(children) < 4:
            return
        columns = [
            children[0:1], children[1:2],
            children[2:3], children[3:4]
        ]
        self._balance_columns(columns)

    def _arrange_position5(self, children: List['Node']) -> None:
        if len(children) < 6:
            return
        columns = [
            children[0:1], children[1:2],
            children[2:3], children[3:4],
            children[4:5], children[5:6]
        ]
        self._balance_columns(columns)

    def _arrange_position7(self, children: List['Node']) -> None:
        if len(children) < 8:
            return
        columns = [
            children[0:1], children[1:2],
            children[2:3], children[3:4],
            children[4:5], children[5:6],
            children[6:7], children[7:8]
        ]
        self._balance_columns(columns)

    def _balance_columns(self, columns: List[List['Node']]) -> None:
        column_sizes = [len(col) for col in columns]
        min_size = min(column_sizes)
        max_size = max(column_sizes)
        if self.bank_number > 0:
            for i in range(len(columns)):
                if column_sizes[i] < max_size and self.bank_number > 0:
                    column_sizes[i] += 1
                    self.bank_number -= 1
        total_diff = 0
        for i in range(len(columns)):
            if column_sizes[i] > min_size:
                diff = column_sizes[i] - min_size
                total_diff += diff
        self.bank_number = min(self.bank_number + total_diff, 2)

# ---------------------------
#　ノード作成・ツリー構築用関数（外部入力可能に変更）
# ---------------------------
def create_nodes_deterministic(layer_config: List[int], fixed_positions: List[int]) -> List[Node]:
    """
    ランダムではなく、固定値を用いてノード群を作成する例。
    layer_config: 各層のノード数のリスト 例：[1, 5, 2, …]
    fixed_positions: 各ノード作成時に適用するポジション番号（たとえば [1,3,5,7] のどれか）
                     ※層毎に同じ値とする簡易例です。
    """
    nodes = []
    node_counter = 1
    layer_nodes: Dict[int, List[Node]] = {0: []}
    
    # ルート層（層0）の作成
    for i in range(layer_config[0]):
        # 固定のポジション番号。インデックス0 から fixed_positions[0] を利用する例
        pos = fixed_positions[0] if fixed_positions else 1
        node = Node(
            name=f"Node_{node_counter}",
            position_number=pos,
            active=True
        )
        nodes.append(node)
        layer_nodes[0].append(node)
        node_counter += 1

    # 第2層以降
    for layer, num_children in enumerate(layer_config[1:], 1):
        layer_nodes[layer] = []
        for parent in layer_nodes[layer - 1]:
            for _ in range(num_children):
                pos = fixed_positions[layer] if layer < len(fixed_positions) else fixed_positions[-1]
                node = Node(
                    name=f"Node_{node_counter}",
                    position_number=pos,
                    parent_node=parent.name,
                    active=True   # 固定でアクティブ
                )
                nodes.append(node)
                layer_nodes[layer].append(node)
                parent.children.append(node)
                node_counter += 1
    return nodes

def build_node_hierarchy(nodes: List[Node]) -> List[Node]:
    node_dict = {node.name: node for node in nodes}
    root_nodes = []
    for node in nodes:
        if node.parent_node:
            if node.parent_node in node_dict:
                parent = node_dict[node.parent_node]
                if node not in parent.children:
                    parent.children.append(node)
        else:
            root_nodes.append(node)
    return root_nodes

def update_tree_numbers(node: Node) -> None:
    node.tree_number = node.calculate_tree_number()
    for child in node.children:
        if child.active:
            update_tree_numbers(child)

def calculate_all_bonuses(nodes: List[Node],
                          bonus_rise_params: Dict[str, float],
                          bonus_pf_params: Dict[str, int]) -> Dict[str, Tuple[int, int]]:
    total_paid_points = sum(node.paid_point for node in nodes)
    bonus_summary = {
        'riseup_binary_bonus': [0, 0],
        'product_free_bonus': [0, 0],
        'matching_bonus': [0, 0],
        'car_bonus': [0, 0],
        'house_bonus': [0, 0],
        'sharing_bonus': [0, 0]
    }

    for node in nodes:
        if not node.active:
            continue
        node.calculate_binary_numbers()

        bonuses = {
            'riseup_binary_bonus': node.calculate_riseup_binary_bonus(bonus_rise_params),
            'product_free_bonus': node.calculate_product_free_bonus(bonus_pf_params),
            'matching_bonus': node.calculate_matching_bonus(bonus_pf_params, total_paid_points),
            'car_bonus': node.calculate_car_bonus(),
            'house_bonus': node.calculate_house_bonus(),
            'sharing_bonus': node.calculate_sharing_bonus(total_paid_points)
        }

        for bonus_type, amount in bonuses.items():
            if amount > 0:
                bonus_summary[bonus_type][0] += amount
                bonus_summary[bonus_type][1] += 1

        node.bonus_point = sum(bonuses.values())
        node.total_bonus_point += node.bonus_point

    return bonus_summary

# ---------------------------
#  Streamlit アプリ本体
# ---------------------------
def main():
    st.title("ボーナス計算シミュレーション")
    st.markdown("外部からパラメータを渡して、固定値を用いたシミュレーションを実行します。")

    st.sidebar.header("シミュレーションパラメータ")
    # １．各層のノード数の設定（カンマ区切りで入力例：1,5,2,2,2）
    layer_config_str = st.sidebar.text_input("各層のノード数（カンマ区切り）", value="1,5,2,2")
    try:
        layer_config = [int(s.strip()) for s in layer_config_str.split(",")]
    except Exception as e:
        st.error("層数はカンマ区切りの整数で入力してください。")
        return

    # ２．各層のポジション番号（カンマ区切り、例：1,3,5,7　※層数に合わせて利用）
    fixed_positions_str = st.sidebar.text_input("各層のポジション番号（カンマ区切り）", value="1,3,5,7")
    try:
        fixed_positions = [int(s.strip()) for s in fixed_positions_str.split(",")]
    except Exception as e:
        st.error("ポジション番号はカンマ区切りの整数で入力してください。")
        return

    # ３．シミュレーション回数
    num_simulations = st.sidebar.number_input("シミュレーション回数", min_value=1, value=2, step=1)

    st.sidebar.subheader("ライズアップボーナスの定数設定")
    bonus_rise_params = {
        "level1": st.sidebar.number_input("level1 (例: 3000)", value=3000.0),
        "level2": st.sidebar.number_input("level2 (例: 4000)", value=4000.0),
        "level3": st.sidebar.number_input("level3 (例: 5000)", value=5000.0),
        "level4": st.sidebar.number_input("level4 (例: 2000)", value=2000.0),
    }

    st.sidebar.subheader("製品無料ボーナスの定数設定")
    bonus_pf_params = {
        "pf4": st.sidebar.number_input("pf4 (例: 10000)", value=10000, step=1000),
        "pf8": st.sidebar.number_input("pf8 (例: 7000)", value=7000, step=1000),
        "pf12": st.sidebar.number_input("pf12 (例: 4000)", value=4000, step=1000),
        "pf16": st.sidebar.number_input("pf16 (例: 1000)", value=1000, step=500),
    }

    # シミュレーション実行ボタン
    if st.sidebar.button("計算開始"):
        st.write("シミュレーション実行中・・・")
        # 固定値を用いてノード群を作成（乱数は使わず同じ設定となる）
        nodes = create_nodes_deterministic(layer_config, fixed_positions)
        # 親子関係の構築
        root_nodes = build_node_hierarchy(nodes)
        # ツリー番号の更新
        for root in root_nodes:
            update_tree_numbers(root)
        # 初期のバイナリー計算
        for node in nodes:
            if node.active:
                node.calculate_binary_numbers()
        st.write("ノード作成完了")

        simulation_results = []

        for sim in range(num_simulations):
            st.write(f"#### シミュレーション {sim+1} 開始")
            # 階層再構築
            root_nodes = build_node_hierarchy(nodes)
            for root in root_nodes:
                root.arrange_tree()
            # タイトルランク更新
            for node in nodes:
                node.update_title_rank()
            # ボーナス計算
            bonus_summary = calculate_all_bonuses(nodes, bonus_rise_params, bonus_pf_params)
            total_bonus = sum(node.bonus_point for node in nodes)
            simulation_results.append((sim+1, bonus_summary, total_bonus))
            st.write("**各ボーナス内訳 [合計金額, 件数]:**")
            st.json(bonus_summary)
            st.write(f"**総ボーナス金額: {total_bonus}**")
            # 次回シミュレーション用に全ノードをアクティブ化＆再計算
            for node in nodes:
                node.activate()
            for node in nodes:
                if node.active:
                    node.calculate_binary_numbers()
            st.write(f"シミュレーション {sim+1} 完了")
            time.sleep(1)

        st.write("### 全シミュレーション結果まとめ")
        for sim, bonus_summary, total_bonus in simulation_results:
            st.write(f"**シミュレーション {sim}**")
            st.write("各ボーナス内訳:")
            st.json(bonus_summary)
            st.write(f"総ボーナス金額: {total_bonus}")

if __name__ == "__main__":
    main()

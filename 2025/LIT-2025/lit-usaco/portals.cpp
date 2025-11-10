#include <bits/stdc++.h>

using namespace std;

const int MAX_N = 20010;
const int MAX_M = 20010;

int n, m, d, q;
struct Portal {
    int a1, l1, r1, a2, l2, r2;
};
vector<Portal> portals;

int SS = 0;
int TT;
int P_IN_BASE;
int P_OUT_BASE;

vector<int> residual_cap;
vector<char> used;

int x, y;
int cap_SS_x, cap_SS_y;

int get_first_multiple(int l, int a) {
    if (a == 0) return -1;
    int mod = l % a;
    if (mod == 0) return l;
    return l + (a - mod);
}

bool dfs(int v) {
    if (v == TT) return true;
    used[v] = true;

    if (v == SS) {
        if (cap_SS_x > 0 && !used[x]) {
            if (dfs(x)) {
                cap_SS_x--;
                return true;
            }
        }
        if (cap_SS_y > 0 && !used[y]) {
            if (dfs(y)) {
                cap_SS_y--;
                return true;
            }
        }
    } else if (1 <= v && v <= n) {
        for (int p = 0; p < m; p++) {
            const Portal& po = portals[p];
            if (po.l1 <= v && v <= po.r1 && (po.a1 == 0 || v % po.a1 == 0)) {
                int pin = P_IN_BASE + p;
                if (!used[pin] && dfs(pin)) {
                    return true;
                }
            }
        }
        if (v == d && !used[TT] && dfs(TT)) {
            return true;
        }
    } else if (P_IN_BASE <= v && v < P_IN_BASE + m) {
        int p = v - P_IN_BASE;
        int pout = P_OUT_BASE + p;
        if (residual_cap[p] > 0 && !used[pout] && dfs(pout)) {
            residual_cap[p]--;
            return true;
        }
    } else if (P_OUT_BASE <= v && v < P_OUT_BASE + m) {
        int p = v - P_OUT_BASE;
        const Portal& po = portals[p];
        int first = get_first_multiple(po.l2, po.a2);
        if (first == -1) return false;
        for (int c = first; c <= po.r2; c += po.a2) {
            if (c < 1 || c > n) continue;
            if (!used[c] && dfs(c)) {
                return true;
            }
        }
    }
    return false;
}

string solve_query(int cx, int cy) {
    x = cx;
    y = cy;

    residual_cap.assign(m, 1);
    cap_SS_x = 1;
    cap_SS_y = 1;
    if (x == y) {
        cap_SS_x = 2;
        cap_SS_y = 0;
    }

    int flow = 0;
    while (true) {
        fill(used.begin(), used.end(), false);
        if (!dfs(SS)) break;
        flow++;
        if (flow == 2) break;
    }

    return (flow == 2) ? "Yes" : "No";
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    cin >> n >> m;
    portals.resize(m);
    for (int i = 0; i < m; i++) {
        cin >> portals[i].a1 >> portals[i].l1 >> portals[i].r1 >> portals[i].a2 >> portals[i].l2 >> portals[i].r2;
    }
    cin >> d >> q;

    TT = n + 1;
    P_IN_BASE = TT + 1;
    P_OUT_BASE = P_IN_BASE + m;
    int total_nodes = P_OUT_BASE + m;

    used.resize(total_nodes + 1);

    for (int i = 0; i < q; i++) {
        int xx, yy;
        cin >> xx >> yy;
        cout << solve_query(xx, yy) << "\n";
    }

    return 0;
}
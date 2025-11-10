#include <iostream>
#include <string>
#include <vector>
#include <cstdint>
#include <unordered_map>
#include <algorithm>
#include <thread>
#include <mutex>
#include <atomic>
#include <functional>

// Use 64-bit integers for large numbers
using int64 = int64_t;

// --- Helper Functions ---
int64 calculate_D_R(int64 xr, int64 yr) {
    std::string a_str = std::to_string(xr);
    std::string b_str = std::to_string(yr);
    a_str = std::string(3 - a_str.length(), '0') + a_str;
    b_str = std::string(3 - b_str.length(), '0') + b_str;

    int a[3], b[3];
    for(int i=0; i<3; ++i) { a[i] = a_str[i] - '0'; b[i] = b_str[i] - '0'; }

    if (a[0] * b[0] < 10 || a[1] * b[1] < 10 || a[2] * b[2] < 10) return -1;
    return std::stoll(std::to_string(a[0] * b[0]) + std::to_string(a[1] * b[1]) + std::to_string(a[2] * b[2]));
}

int64 calculate_D_L(int64 xl, int64 yl) {
    std::string a_str = std::to_string(xl);
    std::string b_str = std::to_string(yl);
    a_str = std::string(5 - a_str.length(), '0') + a_str;
    b_str = std::string(4 - b_str.length(), '0') + b_str;

    int a[5], b[4];
    for(int i=0; i<5; ++i) a[i] = a_str[i] - '0';
    for(int i=0; i<4; ++i) b[i] = b_str[i] - '0';

    if (a[1] * b[0] < 10 || a[2] * b[1] < 10 || a[3] * b[2] < 10 || a[4] * b[3] < 10) return -1;
    return std::stoll(std::to_string(a[0]) + std::to_string(a[1] * b[0]) + std::to_string(a[2] * b[1]) + std::to_string(a[3] * b[2]) + std::to_string(a[4] * b[3]));
}

struct RightHalfInfo { int64 xr, yr, k; };
struct MapValue { int64 xr, yr, yl; };

// --- Thread-safe variables and Worker Function ---
std::mutex solutions_mutex;
std::vector<std::pair<int64, int64>> all_solutions;

void find_solutions_worker(
    int64 xl_start, int64 xl_end, int thread_id,
    const std::unordered_map<int64, std::vector<MapValue>>& map_R,
    const std::vector<int64>& yr_options)
{
    std::vector<std::pair<int64, int64>> local_solutions;
    for (int64 xl = xl_start; xl < xl_end; ++xl) {
        if (thread_id == 0 && xl % 1000 == 0) {
             std::cout << "Main thread probing xl = " << xl << "..." << std::endl;
        }

        for (int64 yl = 1000; yl < 10000; ++yl) {
            int64 dl = calculate_D_L(xl, yl);
            if (dl == -1) continue;

            for (int64 yr : yr_options) {
                int64 lhs_val = 1000 * (dl - xl * yl) - xl * yr;
                auto it = map_R.find(lhs_val);
                if (it != map_R.end()) {
                    for (const auto& rhs_combo : it->second) {
                        if (rhs_combo.yl == yl && rhs_combo.yr == yr) {
                            local_solutions.push_back({xl * 1000 + rhs_combo.xr, yl * 1000 + yr});
                        }
                    }
                }
            }
        }
    }
    // Lock and push local findings to the global vector
    if (!local_solutions.empty()) {
        std::lock_guard<std::mutex> lock(solutions_mutex);
        all_solutions.insert(all_solutions.end(), local_solutions.begin(), local_solutions.end());
    }
}

int main() {
    // Step 1: Find valid (xR, yR) pairs
    std::cout << "Step 1: Finding valid right-half pairs..." << std::endl;
    std::vector<RightHalfInfo> valid_R;
    for (int64 xr = 0; xr < 1000; ++xr) for (int64 yr = 0; yr < 1000; ++yr) {
        int64 dr = calculate_D_R(xr, yr);
        if (dr != -1 && (xr * yr - dr) % 1000 == 0) {
            valid_R.push_back({xr, yr, (xr * yr - dr) / 1000});
        }
    }
    std::cout << "Found " << valid_R.size() << " valid right-half pairs." << std::endl;

    // Step 2: Build map from RHS
    std::cout << "\nStep 2: Building map from right-side variables..." << std::endl;
    std::unordered_map<int64, std::vector<MapValue>> map_R;
    for (const auto& combo : valid_R) for (int64 yl = 1000; yl < 10000; ++yl) {
        map_R[combo.xr * yl + combo.k].push_back({combo.xr, combo.yr, yl});
    }
    std::cout << "Map created with " << map_R.size() << " unique keys." << std::endl;

    // Step 3: Start the parallel search
    std::cout << "\nStep 3: Starting multithreaded search for ALL solutions..." << std::endl;
    unsigned int num_threads = std::thread::hardware_concurrency();
    std::cout << "Using " << num_threads << " threads." << std::endl;
    std::vector<std::thread> threads;

    std::vector<int64> yr_options;
    for(const auto& combo : valid_R) yr_options.push_back(combo.yr);
    std::sort(yr_options.begin(), yr_options.end());
    yr_options.erase(std::unique(yr_options.begin(), yr_options.end()), yr_options.end());

    int64 xl_range = 90000;
    int64 chunk_size = xl_range / num_threads;

    for (unsigned int i = 0; i < num_threads; ++i) {
        int64 start = 10000 + i * chunk_size;
        int64 end = (i == num_threads - 1) ? 100000 : start + chunk_size;
        threads.emplace_back(find_solutions_worker, start, end, i, std::cref(map_R), std::cref(yr_options));
    }

    for (auto& t : threads) {
        t.join();
    }

    // Step 4: Print all results
    if (!all_solutions.empty()) {
        std::cout << "\n-----------------" << std::endl;
        std::cout << "--- " << all_solutions.size() << " SOLUTION(S) FOUND! ---" << std::endl;
        int count = 1;
        for (const auto& sol_pair : all_solutions) {
             std::cout << count++ << ": x = " << sol_pair.first << ", y = " << sol_pair.second << std::endl;
        }
        std::cout << "-----------------" << std::endl;
    } else {
        std::cout << "\n--- No solution found. ---" << std::endl;
    }

    return 0;
}
use std::collections::HashMap;
use rayon::prelude::*;
use indicatif::{ProgressBar, ProgressStyle};

// Helper Functions (No changes needed)
fn get_digits(mut n: i64, num_digits: u32) -> Vec<i64> {
    let mut digits = Vec::new();
    for _ in 0..num_digits {
        digits.push(n % 10);
        n /= 10;
    }
    digits.reverse();
    digits
}

fn calculate_d_r(xr: i64, yr: i64) -> Option<i64> {
    let a = get_digits(xr, 3);
    let b = get_digits(yr, 3);
    if a[0] * b[0] < 10 || a[1] * b[1] < 10 || a[2] * b[2] < 10 {
        return None;
    }
    let dr_str = format!("{}{}{}", a[0] * b[0], a[1] * b[1], a[2] * b[2]);
    dr_str.parse().ok()
}

fn calculate_d_l(xl: i64, yl: i64) -> Option<i64> {
    let a = get_digits(xl, 5);
    let b = get_digits(yl, 4);
    if a[1] * b[0] < 10 || a[2] * b[1] < 10 || a[3] * b[2] < 10 || a[4] * b[3] < 10 {
        return None;
    }
    let dl_str = format!("{}{}{}{}{}", a[0], a[1] * b[0], a[2] * b[1], a[3] * b[2], a[4] * b[3]);
    dl_str.parse().ok()
}

struct RightHalfInfo { xr: i64, yr: i64, k: i64 }
struct MapValue { xr: i64, yr: i64, yl: i64 }

fn main() {
    // Step 1 & 2 are identical
    println!("Step 1: Finding valid right-half pairs (in parallel)...");
    let valid_r: Vec<RightHalfInfo> = (0..1000).into_par_iter().flat_map(|xr| {
        (0..1000).into_par_iter().filter_map(move |yr| {
            if let Some(dr) = calculate_d_r(xr, yr) {
                if (xr * yr - dr) % 1000 == 0 {
                    return Some(RightHalfInfo { xr, yr, k: (xr * yr - dr) / 1000 });
                }
            }
            None
        })
    }).collect();
    println!("Found {} valid right-half pairs.", valid_r.len());

    println!("\nStep 2: Building map from right-side variables...");
    let mut map_r: HashMap<i64, Vec<MapValue>> = HashMap::new();
    for combo in &valid_r {
        for yl in 1000..10000 {
            map_r.entry(combo.xr * yl + combo.k).or_default().push(MapValue {
                xr: combo.xr, yr: combo.yr, yl,
            });
        }
    }
    println!("Map created with {} unique keys.", map_r.len());

    // Step 3: MODIFIED to find all solutions
    println!("\nStep 3: Starting parallel search for ALL solutions...");
    let mut yr_options: Vec<i64> = valid_r.iter().map(|c| c.yr).collect();
    yr_options.sort_unstable();
    yr_options.dedup();

    let style = ProgressStyle::default_bar()
        .template("{spinner:.green} [{elapsed_precise}] [{bar:40.cyan/blue}] {pos:>7}/{len:7} ({eta})")
        .unwrap();
    let pb = ProgressBar::new(90000).with_style(style);

    // MODIFICATION: Use flat_map to collect all results, not just the first one.
    let solutions: Vec<(i64, i64)> = (10000..100000).into_par_iter().flat_map(|xl| {
        pb.inc(1);
        let mut found_pairs = Vec::new(); // Store pairs found for this xl
        for yl in 1000..10000 {
            if let Some(dl) = calculate_d_l(xl, yl) {
                for &yr in &yr_options {
                    let lhs_val = 1000 * (dl - xl * yl) - xl * yr;
                    if let Some(rhs_combos) = map_r.get(&lhs_val) {
                        for rhs_combo in rhs_combos {
                            if rhs_combo.yl == yl && rhs_combo.yr == yr {
                                // Instead of returning, add the pair to our list
                                found_pairs.push((xl * 1000 + rhs_combo.xr, yl * 1000 + yr));
                            }
                        }
                    }
                }
            }
        }
        // Return the list of pairs found for this xl. `flat_map` will merge them all.
        found_pairs
    }).collect();
    pb.finish_with_message("Search complete.");

    // Step 4: MODIFIED to print all solutions
    if !solutions.is_empty() {
        println!("\n-----------------");
        println!("--- {} SOLUTION(S) FOUND! ---", solutions.len());
        for (i, (x_sol, y_sol)) in solutions.iter().enumerate() {
            println!("{:>3}: x = {}, y = {}", i + 1, x_sol, y_sol);
        }
        println!("-----------------");
    } else {
        println!("\n--- No solution found. ---");
    }
}
from elo import calculate_new_ratings

r1 = 1020
r2 = 1020

r1, r2 = calculate_new_ratings(r1, r2, 1, 40)

print(r1, r2)
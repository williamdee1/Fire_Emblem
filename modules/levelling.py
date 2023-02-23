import pandas as pd
import numpy as np


def level_up(base_stats, char_growth, char,                             # character-specific metrics
             class_base, class_growth, class_max,                       # class-specific metrics
             int_tgt, promo_class, base_tgt,                            # promotion choices
             sg_cols, cat_dict):                                        # other info

    # Return character base stats and info as DataFrame:
    char_base = base_stats[base_stats.Name == char].reset_index(drop=True)

    # Initialize based on current character details (i.e. promote, return initial growth points in stats)
    char_base, char_lev, growth_p, class_growth = init_char(char_base, char, char_growth,
                                                            class_base, class_growth, class_max,
                                                            promo_class, base_tgt, sg_cols)

    # Add new column displaying characters internal level:
    char_base['int_lev'] = char_lev

    # Levelling loop:
    while char_lev < int_tgt:
        # Current character and class variables:
        char_g, char_lev, char_class = char_stats(char_base, char_growth, char, sg_cols)
        class_type, _, class_g = class_stats(class_base, char_class, class_growth, class_max, sg_cols)

        # Return stat growth based on current class:
        stat_g = pd.DataFrame(np.add(char_g, class_g), columns = sg_cols)
        # Add to existing growth points:
        growth_p = growth_p + stat_g

        # Add new row to dataframe to hold level-up stats:
        new_data = pd.DataFrame(char_base[-1:].values, columns=char_base.columns)
        char_base = pd.concat([char_base, new_data], ignore_index=True)

        # --- GROW STATS ---#
        for col in sg_cols:
            # Extract individual stat values:
            stat = growth_p[col][0]
            # If growth points in stat are > 100, +1 to stat and remove 100 growth points:
            if stat > 100:
                # Check if stat is already at max:
                if char_base.loc[char_base.index[-1], col] >= class_max[class_max['Name']==char_class][col].values[0]:
                    pass
                else:
                    char_base.loc[char_base.index[-1], col] += 1.0
                    growth_p[col] -= 100

        # Increase character levels and return new level:
        char_base.loc[char_base.index[-1], ['Level', 'int_lev']] += 1.0
        char_base, char_lev = check_promo(char_base, char_class, char, class_base, class_type, promo_class, base_tgt, sg_cols)

    # Add rating columns:
    char_base['game_rt'] = np.sum(char_base[sg_cols[1:]], axis=1)
    class_cat = class_base[class_base['Name'] == char_base['Class'][-1:].values[0]]['Cat'].values[0]
    char_base['promo_rt'] = round(np.sum(char_base[sg_cols] * cat_dict[class_cat], axis=1))
    char_base = char_base.drop(['Internal'], axis=1)

    return char_base


def init_char(char_base, char, char_growth, class_base, class_growth, class_max, promo_class, base_tgt, sg_cols):
    # Return current char and class stats:
    _, char_lev, char_class = char_stats(char_base, char_growth, char, sg_cols)
    class_type, _, _ = class_stats(class_base, char_class, class_growth, class_max, sg_cols)
    # Double class growth rates if character is Jean (due to his ability - Expertise):
    if char == 'Jean':
        class_growth[sg_cols] = class_growth[sg_cols] * 2

    # If character is in a Basic class and >= level 10, promote immediately to Advanced class:
    if char_lev >= base_tgt and class_type == 'Base':
        # Check if there's a pre-requisite for the Advanced promotion:
        promo_class = check_prereq(class_base, char_class, promo_class)
        # Promote character:
        char_base = promote(char_base, char_class, char, class_base, promo_class, sg_cols)

    # If the character is an Advanced/Special class which is not desired, use a Second Seal to alter immediately:
    elif class_type != 'Base' and char_class != promo_class:
        # Check if there's a pre-requisite for the Advanced promotion:
        promo_class = check_prereq(class_base, char_class, promo_class)
        # Promote character:
        char_base = promote(char_base, char_class, char, class_base, promo_class, sg_cols)

        # Add any internal levels that the character may have already been trained (i.e. Vander):
    char_lev += char_base['Internal'][0]

    # Update character and class growth and return characters initial growth points:
    char_g, _, _ = char_stats(char_base, char_growth, char, sg_cols)
    _, _, class_g = class_stats(class_base, char_class, class_growth, class_max, sg_cols)
    growth_p = pd.DataFrame(np.add(char_g, class_g), columns=sg_cols)

    return char_base, char_lev, growth_p, class_growth


def check_promo(char_base, char_class, char, class_base, class_type, promo_class, base_tgt, sg_cols):
    # If character is in a Basic class and >= level 10, promote immediately to Advanced class:
    if char_base['Level'][-1:].values[0] == base_tgt and class_type == 'Base':
        # Check if there's a pre-requisite for the Advanced promotion:
        # promo_class = check_prereq(class_base, char_class, promo_class)
        # ! Removed as realised char can be promoted at 10 and then second sealed between adv. classes.
        # Promote character:
        char_base = promote(char_base, char_class, char, class_base, promo_class, sg_cols)

    elif char_base['Level'][-1:].values[0] == 20 and class_type == 'Advanced':
        # Promote character:
        char_base = promote(char_base, char_class, char, class_base, promo_class, sg_cols)

    elif char_base['Level'][-1:].values[0] == 40 and class_type == 'Special':
        # Promote character:
        char_base = promote(char_base, char_class, char, class_base, promo_class, sg_cols)

    char_lev = int(char_base.loc[char_base.index[-1], 'int_lev'])

    return char_base, char_lev


def check_prereq(class_base, char_class, promo_class):
    # Return the pre-requisite for using a Master Seal:
    pre_req = class_base[class_base['Name'] == promo_class]['Pre_req'].values[0]

    # If the characters base class is already the req. class, then can use Master Seal and promote normally:
    if char_class in pre_req or pre_req == 'None':
        pass
    # If not, then must use a second seal to change class, before character can be promoted at level 10:
    else:
        reqs = pre_req.split(', ')
        # Account for pre-required classes like "Sword Cavalier, Lance Cavalier, Axe Cavalier":
        if len(reqs) > 1:
            if char_class.split(' ')[0] in 'Sword, Axe, Lance':
                promo_class = char_class.split(' ')[0] + " " + reqs[0].split(' ')[-1]
            else:
                promo_class = reqs[0]

        else:
            promo_class = pre_req

    return promo_class


def char_stats(char_base, char_growth, char, sg_cols):
    # Extract character-specific info -> Growth, level & current class:
    char_g = char_growth[char_growth.Name == char][sg_cols].values
    char_lev = char_base['Level'][-1:].values[0]
    char_class = char_base['Class'][-1:].values[0]

    return char_g, char_lev, char_class


def class_stats(class_base, char_class, class_growth, class_max, sg_cols):
    # Extract class-specific info -> Type (Basic or Advanced), max_stats & growth:
    class_type = class_base[class_base['Name'] == char_class]['Type'].values[0]
    class_max = class_max[class_max['Name'] == char_class][sg_cols].values
    class_g = class_growth[class_growth['Name'] == char_class][sg_cols].values

    return class_type, class_max, class_g


def promote(char_base, char_class, char, class_base, promo_class, sg_cols):
    # Reset level and promote to selected Advanced class:
    char_base['Level'][-1:] = 1
    char_base['Class'][-1:] = promo_class
    # Calculate class base differences and update underlying stats:
    class_diffs = change_class(char_class, char, class_base, promo_class, sg_cols)
    char_base.loc[char_base.index[-1]][sg_cols] += class_diffs

    return char_base


def change_class(char_class, char, class_base, promo_class, sg_cols):
    cb_curr = class_base[class_base['Name'] == char_class]

    # Extracting unique class info:
    if len(cb_curr) > 1:
        cb_curr = cb_curr[cb_curr['Unique'] == char]

    cb_new = class_base[class_base['Name'] == promo_class]

    # Calculate class base stat differences:
    diffs = cb_new[sg_cols].iloc[0] - cb_curr[sg_cols].iloc[0]

    return diffs
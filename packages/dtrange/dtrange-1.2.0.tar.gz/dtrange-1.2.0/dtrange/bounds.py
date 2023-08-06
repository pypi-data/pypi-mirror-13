def bounds(items, item):
    ''' Binary search bracketing indices.
    
    Parameters
    ----------
    items : list
        Ascending sorted items.
    item : comparable object
    
    Returns
    -------
    [lower, upper) half-open indices
    '''    
    n_1 = len(items) - 1
    if n_1 < 0:
        return None, None
    if item <= items[0]:
        return 0,0
    if item >= items[-1]:
        return n_1, n_1

    left, right = 0, n_1
    while left <= right:
        mid = int((left + right) / 2)
        if items[mid] == item:
            break
        elif items[mid] < item:
            left = mid + 1
        else:
            right = mid - 1
            
    if right < left:
        left = right
    else:
        left = mid
           
    right = min(n_1, left + 1)
    if items[left] <= item and item <= items[right]:
        return left, right
    else:
        return None, None

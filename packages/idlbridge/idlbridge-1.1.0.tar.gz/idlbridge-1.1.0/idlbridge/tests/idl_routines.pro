pro idl_test_procedure, a, b, c, d, key_a=ka, key_b=kb

    if keyword_set(ka) then begin

        a = 20
        b = 40
        c = 60
        d = 80

    endif

    if keyword_set(kb) then begin

        a = 1000
        b = 2000
        c = 3000
        d = 4000

    endif

    a = b
    b = c
    c = d
    d = 0.0

end


function idl_test_function, a, b, c, d, key_a=ka, key_b=kb

    if keyword_set(ka) then begin

        a = 20
        b = 40
        c = 60
        d = 80
        return, 100

    endif

    if keyword_set(kb) then begin

        a = 1000
        b = 2000
        c = 3000
        d = 4000
        return, 5000

    endif

    a = b
    b = c
    c = d
    d = 0.0

    return, 999

end

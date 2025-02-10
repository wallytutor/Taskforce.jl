module Common

function remove_spaces(list)
    return filter(x -> x != "", list)
end

function uncomment(line; comment_char = "!")
    !startswith(line, comment_char) && return line
    return line[length(comment_char)+1:end]
end

end # (Common)
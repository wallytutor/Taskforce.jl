module Elmer

using DataFrames
using DelimitedFiles
using CairoMakie

import ..Common

export get_convergence_history

function get_convergence_header(fname)
    open(fname) do fp
        line = readline(fp)

        if !startswith(line, "!")
            error("""\
                Not a convergence file; it is expected to start by a \
                `!` indicating a comment: got $(line[1])
                """)
        end
        
        line = Common.uncomment(line)
        line = split(line, " ")
        line = Common.remove_spaces(line)
        return line
    end
end

function get_convergence_history(fname)
    data = readdlm(fname; skipstart=1)
    header = get_convergence_header(fname)
    return DataFrame(data, header)
end

end # (Elmer)
module Fluent

using DataFrames
using DelimitedFiles: readdlm
using Statistics: mean

import ..Common

#######################################################################
# API
#######################################################################

function read_report(filename; n_last::Int = -1, header_number::Int = 3)
    header = get_report_header(filename, header_number)
    data = get_report_data(filename, header_number, n_last)
    return DataFrame(data, header)
end

#######################################################################
# INTERNALS
#######################################################################

function get_report_header(filename::String, header_number::Int)
    line = Common.read_specific_row(filename, header_number)
    matches = eachmatch(r"\"([^\"]*)\"", line)
    return String.(map(m->first(m.captures), matches))
end

function get_report_data(filename::String, header_number::Int, n_last::Int)
    n_last <= 0 && return readdlm(filename; skipstart=header_number)

    n_lines = Common.count_lines(filename)
    n = min(n_lines-header_number, n_last)
    return Common.get_last_lines(filename, n)
end

end
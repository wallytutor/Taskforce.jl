module Common

using DataFrames
using DelimitedFiles
using CairoMakie

const MAKIETHEME = Theme(
	fontsize = 10,

	# https://juliagraphics.github.io/Colors.jl/stable/namedcolors/
	palette = (
		color = [
			# Start with classy black...
			:black,

			# Classic colors...
			:red, 
			:blue,
			:green,

			# Degraded classics...
			:tomato1,
			:slateblue1,
			:chartreuse1,
		],
	),

    Axis = (
		# Background:
		backgroundcolor = :gray98,
	
		# Grids:
        xgridcolor = :gray20,
        ygridcolor = :gray20,
		xgridstyle = :dot,
		ygridstyle = :dot,
		xgridwidth = 0.8,
		ygridwidth = 0.8,

		# Spines:
        leftspinevisible   = true,
        rightspinevisible  = true,
        bottomspinevisible = true,
        topspinevisible    = true,
    )
)

function remove_spaces(list)
    return filter(x -> x != "", list)
end

function uncomment(line; comment_char = "!")
    !startswith(line, comment_char) && return line
    return line[length(comment_char)+1:end]
end

function set_type!(df, column, totype)
	!(column in names(df)) && return
	transform!(df, column => ByRow(x -> convert(totype, x)) => column)
	return nothing
end

function read_specific_row(filename::String, row_number::Int)
    line = open(filename) do file
        current_row = 1

        for line in eachline(file)
            current_row == row_number && return line
            current_row += 1
        end
    end

    isnothing(line) && error("Row number out of range")
    return line
end

function count_lines(filename::String)
    return open(filename) do fp
        sum(_->1, eachline(fp))
    end
end

function get_last_lines(filename::String, n::Int)
    last_n_lines = open(filename) do file
        all_lines = readlines(file)
        return all_lines[end-n+1:end]
    end

    combined_lines = join(last_n_lines, "\n")
    data = readdlm(IOBuffer(combined_lines))

    return data
end

end # (Common)
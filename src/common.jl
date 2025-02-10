module Common

using DataFrames


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

end # (Common)
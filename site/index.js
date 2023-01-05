var canvas = document.getElementById("output_image");
canvas.width = 256;
canvas.height = 16;

// Initialize the canvas to be black
var ctx = canvas.getContext("2d")
ctx.fillStyle = "#000000"
ctx.fillRect(0, 0, 256, 16)

// Steps in the generation process
// Each item has `element` and `type`
var items = []

function placeholder() {
	alert("hi, this does not work yet, sorry");
}

function generate() {
	
}
module b02(rst, clk, linea, u);

input clk;
input rst;
input linea;
output reg u;



parameter A = 0;
parameter B = 1;
parameter C = 2;
parameter D = 3;
parameter E = 4;
parameter F = 5;
parameter G = 6;
reg [2:0] stato;
always @(posedge clk, posedge rst) begin //was :always @(posedge clk) begin
    
	
    if(rst == 1'b1) begin
		stato <= A;
		u <= 1'b0;
		end else begin
		case(stato)
			A : begin
				stato <= B;
				u <= 1'b0;
			end
			B : begin
				if(linea == 1'b0) begin
					stato <= C;
				end
				else begin
					stato <= F;
				end
				u <= 1'b0;
			end
			C : begin
				if(linea == 1'b0) begin
					stato <= D;
				end
				else begin
					stato <= G;
				end
				u <= 1'b0;
			end
			D : begin
				stato <= E;
				u <= 1'b0;
			end
			E : begin
				stato <= B;
				u <= 1'b1;
			end
			F : begin
				stato <= G;
				u <= 1'b0;
			end
			G : begin
				if(linea == 1'b0) begin
					stato <= E;
				end
				else begin
					stato <= A;
				end
				u <= 1'b0;
			end
		endcase
	end
end


endmodule

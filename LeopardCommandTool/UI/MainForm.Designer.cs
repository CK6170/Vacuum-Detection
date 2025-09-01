using System.Windows.Forms;

namespace LeopardCommandTool.UI
{
	partial class MainForm
	{
		private System.ComponentModel.IContainer components = null;

		protected override void Dispose(bool disposing)
		{
			if (disposing && (components != null))
			{
				components.Dispose();
			}
			base.Dispose(disposing);
		}

		private void InitializeComponent()
		{
			this.txtPabPortSerialNumber = new System.Windows.Forms.TextBox();
			this.label1 = new System.Windows.Forms.Label();
			this.txtLeopardSequence = new System.Windows.Forms.TextBox();
			this.label2 = new System.Windows.Forms.Label();
			this.txtOpCode = new System.Windows.Forms.TextBox();
			this.label3 = new System.Windows.Forms.Label();
			this.txtSequenceNumber = new System.Windows.Forms.TextBox();
			this.label4 = new System.Windows.Forms.Label();
			this.txtTimestamp = new System.Windows.Forms.TextBox();
			this.label5 = new System.Windows.Forms.Label();
			this.txtLeopardSequenceNumber = new System.Windows.Forms.TextBox();
			this.label6 = new System.Windows.Forms.Label();
			this.btnBuildOpcode = new System.Windows.Forms.Button();
			this.txtOutput = new System.Windows.Forms.TextBox();
			this.btnBuildLeopard = new System.Windows.Forms.Button();
			this.txtLeopardCmd = new System.Windows.Forms.TextBox();
			this.label7 = new System.Windows.Forms.Label();
			this.txtLeopardId = new System.Windows.Forms.TextBox();
			this.label8 = new System.Windows.Forms.Label();
			this.txtLeopardCommand = new System.Windows.Forms.TextBox();
			this.label9 = new System.Windows.Forms.Label();
			this.btnCopy = new System.Windows.Forms.Button();
			this.SuspendLayout();
			// 
			// txtPabPortSerialNumber
			// 
			this.txtPabPortSerialNumber.Location = new System.Drawing.Point(16, 32);
			this.txtPabPortSerialNumber.Name = "txtPabPortSerialNumber";
			this.txtPabPortSerialNumber.PlaceholderText = "pabPortSerialNumber (ushort)";
			this.txtPabPortSerialNumber.Size = new System.Drawing.Size(240, 23);
			this.txtPabPortSerialNumber.TabIndex = 0;
			// 
			// label1
			// 
			this.label1.AutoSize = true;
			this.label1.Location = new System.Drawing.Point(16, 14);
			this.label1.Name = "label1";
			this.label1.Size = new System.Drawing.Size(135, 15);
			this.label1.TabIndex = 1;
			this.label1.Text = "pabPortSerialNumber*";
			// 
			// txtLeopardSequence
			// 
			this.txtLeopardSequence.Location = new System.Drawing.Point(16, 88);
			this.txtLeopardSequence.Name = "txtLeopardSequence";
			this.txtLeopardSequence.PlaceholderText = "leopardSequence (hex bytes, e.g. 01 02 03)";
			this.txtLeopardSequence.Size = new System.Drawing.Size(520, 23);
			this.txtLeopardSequence.TabIndex = 2;
			// 
			// label2
			// 
			this.label2.AutoSize = true;
			this.label2.Location = new System.Drawing.Point(16, 70);
			this.label2.Name = "label2";
			this.label2.Size = new System.Drawing.Size(104, 15);
			this.label2.TabIndex = 3;
			this.label2.Text = "leopardSequence*";
			// 
			// txtOpCode
			// 
			this.txtOpCode.Location = new System.Drawing.Point(272, 32);
			this.txtOpCode.Name = "txtOpCode";
			this.txtOpCode.PlaceholderText = "opCode (ushort, default 1)";
			this.txtOpCode.Size = new System.Drawing.Size(128, 23);
			this.txtOpCode.TabIndex = 1;
			// 
			// label3
			// 
			this.label3.AutoSize = true;
			this.label3.Location = new System.Drawing.Point(272, 14);
			this.label3.Name = "label3";
			this.label3.Size = new System.Drawing.Size(54, 15);
			this.label3.TabIndex = 5;
			this.label3.Text = "opCode";
			// 
			// txtSequenceNumber
			// 
			this.txtSequenceNumber.Location = new System.Drawing.Point(416, 32);
			this.txtSequenceNumber.Name = "txtSequenceNumber";
			this.txtSequenceNumber.PlaceholderText = "sequenceNumber (ushort)";
			this.txtSequenceNumber.Size = new System.Drawing.Size(120, 23);
			this.txtSequenceNumber.TabIndex = 6;
			// 
			// label4
			// 
			this.label4.AutoSize = true;
			this.label4.Location = new System.Drawing.Point(416, 14);
			this.label4.Name = "label4";
			this.label4.Size = new System.Drawing.Size(102, 15);
			this.label4.TabIndex = 7;
			this.label4.Text = "sequenceNumber";
			// 
			// txtTimestamp
			// 
			this.txtTimestamp.Location = new System.Drawing.Point(552, 32);
			this.txtTimestamp.Name = "txtTimestamp";
			this.txtTimestamp.PlaceholderText = "timestamp (uint)";
			this.txtTimestamp.Size = new System.Drawing.Size(136, 23);
			this.txtTimestamp.TabIndex = 8;
			// 
			// label5
			// 
			this.label5.AutoSize = true;
			this.label5.Location = new System.Drawing.Point(552, 14);
			this.label5.Name = "label5";
			this.label5.Size = new System.Drawing.Size(66, 15);
			this.label5.TabIndex = 9;
			this.label5.Text = "timestamp";
			// 
			// txtLeopardSequenceNumber
			// 
			this.txtLeopardSequenceNumber.Location = new System.Drawing.Point(704, 32);
			this.txtLeopardSequenceNumber.Name = "txtLeopardSequenceNumber";
			this.txtLeopardSequenceNumber.PlaceholderText = "leopardSequenceNumber (uint)";
			this.txtLeopardSequenceNumber.Size = new System.Drawing.Size(168, 23);
			this.txtLeopardSequenceNumber.TabIndex = 10;
			// 
			// label6
			// 
			this.label6.AutoSize = true;
			this.label6.Location = new System.Drawing.Point(704, 14);
			this.label6.Name = "label6";
			this.label6.Size = new System.Drawing.Size(138, 15);
			this.label6.TabIndex = 11;
			this.label6.Text = "leopardSequenceNumber";
			// 
			// btnBuildOpcode
			// 
			this.btnBuildOpcode.Location = new System.Drawing.Point(552, 84);
			this.btnBuildOpcode.Name = "btnBuildOpcode";
			this.btnBuildOpcode.Size = new System.Drawing.Size(160, 32);
			this.btnBuildOpcode.TabIndex = 12;
			this.btnBuildOpcode.Text = "Build Opcode Command";
			this.btnBuildOpcode.UseVisualStyleBackColor = true;
			this.btnBuildOpcode.Click += new System.EventHandler(this.btnBuildOpcode_Click);
			// 
			// txtOutput
			// 
			this.txtOutput.Location = new System.Drawing.Point(16, 128);
			this.txtOutput.Multiline = true;
			this.txtOutput.Name = "txtOutput";
			this.txtOutput.PlaceholderText = "Output hex";
			this.txtOutput.ScrollBars = System.Windows.Forms.ScrollBars.Vertical;
			this.txtOutput.Size = new System.Drawing.Size(856, 112);
			this.txtOutput.TabIndex = 13;
			// 
			// btnBuildLeopard
			// 
			this.btnBuildLeopard.Location = new System.Drawing.Point(16, 312);
			this.btnBuildLeopard.Name = "btnBuildLeopard";
			this.btnBuildLeopard.Size = new System.Drawing.Size(224, 32);
			this.btnBuildLeopard.TabIndex = 14;
			this.btnBuildLeopard.Text = "Build Leopard Sequence + CRC16";
			this.btnBuildLeopard.UseVisualStyleBackColor = true;
			this.btnBuildLeopard.Click += new System.EventHandler(this.btnBuildLeopard_Click);
			// 
			// txtLeopardCmd
			// 
			this.txtLeopardCmd.Location = new System.Drawing.Point(16, 272);
			this.txtLeopardCmd.Multiline = true;
			this.txtLeopardCmd.Name = "txtLeopardCmd";
			this.txtLeopardCmd.PlaceholderText = "Leopard packet hex output";
			this.txtLeopardCmd.ScrollBars = System.Windows.Forms.ScrollBars.Vertical;
			this.txtLeopardCmd.Size = new System.Drawing.Size(856, 32);
			this.txtLeopardCmd.TabIndex = 15;
			// 
			// label7
			// 
			this.label7.AutoSize = true;
			this.label7.Location = new System.Drawing.Point(16, 352);
			this.label7.Name = "label7";
			this.label7.Size = new System.Drawing.Size(162, 15);
			this.label7.TabIndex = 16;
			this.label7.Text = "Leopard command builder:";
			// 
			// txtLeopardId
			// 
			this.txtLeopardId.Location = new System.Drawing.Point(16, 384);
			this.txtLeopardId.Name = "txtLeopardId";
			this.txtLeopardId.PlaceholderText = "ID (single ASCII char)";
			this.txtLeopardId.Size = new System.Drawing.Size(176, 23);
			this.txtLeopardId.TabIndex = 17;
			// 
			// label8
			// 
			this.label8.AutoSize = true;
			this.label8.Location = new System.Drawing.Point(16, 366);
			this.label8.Name = "label8";
			this.label8.Size = new System.Drawing.Size(22, 15);
			this.label8.TabIndex = 18;
			this.label8.Text = "ID";
			// 
			// txtLeopardCommand
			// 
			this.txtLeopardCommand.Location = new System.Drawing.Point(208, 384);
			this.txtLeopardCommand.Name = "txtLeopardCommand";
			this.txtLeopardCommand.PlaceholderText = "Command (single ASCII char)";
			this.txtLeopardCommand.Size = new System.Drawing.Size(176, 23);
			this.txtLeopardCommand.TabIndex = 19;
			// 
			// label9
			// 
			this.label9.AutoSize = true;
			this.label9.Location = new System.Drawing.Point(208, 366);
			this.label9.Name = "label9";
			this.label9.Size = new System.Drawing.Size(63, 15);
			this.label9.TabIndex = 20;
			this.label9.Text = "Command";
			// 
			// btnCopy
			// 
			this.btnCopy.Location = new System.Drawing.Point(720, 248);
			this.btnCopy.Name = "btnCopy";
			this.btnCopy.Size = new System.Drawing.Size(152, 22);
			this.btnCopy.TabIndex = 21;
			this.btnCopy.Text = "Copy Hex";
			this.btnCopy.UseVisualStyleBackColor = true;
			this.btnCopy.Click += new System.EventHandler(this.btnCopy_Click);
			// 
			// MainForm
			// 
			this.AutoScaleDimensions = new System.Drawing.SizeF(7F, 15F);
			this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
			this.ClientSize = new System.Drawing.Size(896, 432);
			this.Controls.Add(this.btnCopy);
			this.Controls.Add(this.label9);
			this.Controls.Add(this.txtLeopardCommand);
			this.Controls.Add(this.label8);
			this.Controls.Add(this.txtLeopardId);
			this.Controls.Add(this.label7);
			this.Controls.Add(this.txtLeopardCmd);
			this.Controls.Add(this.btnBuildLeopard);
			this.Controls.Add(this.txtOutput);
			this.Controls.Add(this.btnBuildOpcode);
			this.Controls.Add(this.label6);
			this.Controls.Add(this.txtLeopardSequenceNumber);
			this.Controls.Add(this.label5);
			this.Controls.Add(this.txtTimestamp);
			this.Controls.Add(this.label4);
			this.Controls.Add(this.txtSequenceNumber);
			this.Controls.Add(this.label3);
			this.Controls.Add(this.txtOpCode);
			this.Controls.Add(this.label2);
			this.Controls.Add(this.txtLeopardSequence);
			this.Controls.Add(this.label1);
			this.Controls.Add(this.txtPabPortSerialNumber);
			this.Name = "MainForm";
			this.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen;
			this.Text = "Leopard Command Tool";
			this.ResumeLayout(false);
			this.PerformLayout();
		}

		private TextBox txtPabPortSerialNumber;
		private Label label1;
		private TextBox txtLeopardSequence;
		private Label label2;
		private TextBox txtOpCode;
		private Label label3;
		private TextBox txtSequenceNumber;
		private Label label4;
		private TextBox txtTimestamp;
		private Label label5;
		private TextBox txtLeopardSequenceNumber;
		private Label label6;
		private Button btnBuildOpcode;
		private TextBox txtOutput;
		private Button btnBuildLeopard;
		private TextBox txtLeopardCmd;
		private Label label7;
		private TextBox txtLeopardId;
		private Label label8;
		private TextBox txtLeopardCommand;
		private Label label9;
		private Button btnCopy;
	}
}


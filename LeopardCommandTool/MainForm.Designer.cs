using System.Windows.Forms;

namespace LeopardCommandTool
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
			this.groupBox1 = new GroupBox();
			this.txtLeopardSequenceNumber = new TextBox();
			this.label6 = new Label();
			this.txtTimestamp = new TextBox();
			this.label5 = new Label();
			this.txtSequenceNumber = new TextBox();
			this.label4 = new Label();
			this.txtOpCode = new TextBox();
			this.label3 = new Label();
			this.txtLeopardSequence = new TextBox();
			this.label2 = new Label();
			this.txtPabPortSerialNumber = new TextBox();
			this.label1 = new Label();
			this.btnBuildOpcode = new Button();
			this.txtOpcodeCommandHex = new TextBox();
			this.groupBox2 = new GroupBox();
			this.lblCrcValue = new Label();
			this.txtCrcPacketHex = new TextBox();
			this.btnBuildCrcPacket = new Button();
			this.txtCommand = new TextBox();
			this.label8 = new Label();
			this.txtId = new TextBox();
			this.label7 = new Label();
			this.groupBox1.SuspendLayout();
			this.groupBox2.SuspendLayout();
			this.SuspendLayout();
			// 
			// groupBox1
			// 
			this.groupBox1.Controls.Add(this.txtLeopardSequenceNumber);
			this.groupBox1.Controls.Add(this.label6);
			this.groupBox1.Controls.Add(this.txtTimestamp);
			this.groupBox1.Controls.Add(this.label5);
			this.groupBox1.Controls.Add(this.txtSequenceNumber);
			this.groupBox1.Controls.Add(this.label4);
			this.groupBox1.Controls.Add(this.txtOpCode);
			this.groupBox1.Controls.Add(this.label3);
			this.groupBox1.Controls.Add(this.txtLeopardSequence);
			this.groupBox1.Controls.Add(this.label2);
			this.groupBox1.Controls.Add(this.txtPabPortSerialNumber);
			this.groupBox1.Controls.Add(this.label1);
			this.groupBox1.Controls.Add(this.btnBuildOpcode);
			this.groupBox1.Controls.Add(this.txtOpcodeCommandHex);
			this.groupBox1.Location = new System.Drawing.Point(12, 12);
			this.groupBox1.Name = "groupBox1";
			this.groupBox1.Size = new System.Drawing.Size(760, 260);
			this.groupBox1.TabIndex = 0;
			this.groupBox1.TabStop = false;
			this.groupBox1.Text = "Opcode Command";
			// 
			// txtLeopardSequenceNumber
			// 
			this.txtLeopardSequenceNumber.Location = new System.Drawing.Point(606, 58);
			this.txtLeopardSequenceNumber.Name = "txtLeopardSequenceNumber";
			this.txtLeopardSequenceNumber.Size = new System.Drawing.Size(140, 23);
			this.txtLeopardSequenceNumber.TabIndex = 13;
			// 
			// label6
			// 
			this.label6.AutoSize = true;
			this.label6.Location = new System.Drawing.Point(451, 61);
			this.label6.Name = "label6";
			this.label6.Size = new System.Drawing.Size(149, 15);
			this.label6.TabIndex = 12;
			this.label6.Text = "Leopard Sequence Number";
			// 
			// txtTimestamp
			// 
			this.txtTimestamp.Location = new System.Drawing.Point(606, 22);
			this.txtTimestamp.Name = "txtTimestamp";
			this.txtTimestamp.Size = new System.Drawing.Size(140, 23);
			this.txtTimestamp.TabIndex = 11;
			// 
			// label5
			// 
			this.label5.AutoSize = true;
			this.label5.Location = new System.Drawing.Point(539, 25);
			this.label5.Name = "label5";
			this.label5.Size = new System.Drawing.Size(61, 15);
			this.label5.TabIndex = 10;
			this.label5.Text = "Timestamp";
			// 
			// txtSequenceNumber
			// 
			this.txtSequenceNumber.Location = new System.Drawing.Point(386, 58);
			this.txtSequenceNumber.Name = "txtSequenceNumber";
			this.txtSequenceNumber.Size = new System.Drawing.Size(140, 23);
			this.txtSequenceNumber.TabIndex = 9;
			// 
			// label4
			// 
			this.label4.AutoSize = true;
			this.label4.Location = new System.Drawing.Point(283, 61);
			this.label4.Name = "label4";
			this.label4.Size = new System.Drawing.Size(97, 15);
			this.label4.TabIndex = 8;
			this.label4.Text = "Sequence Number";
			// 
			// txtOpCode
			// 
			this.txtOpCode.Location = new System.Drawing.Point(386, 22);
			this.txtOpCode.Name = "txtOpCode";
			this.txtOpCode.Size = new System.Drawing.Size(140, 23);
			this.txtOpCode.TabIndex = 7;
			// 
			// label3
			// 
			this.label3.AutoSize = true;
			this.label3.Location = new System.Drawing.Point(331, 25);
			this.label3.Name = "label3";
			this.label3.Size = new System.Drawing.Size(49, 15);
			this.label3.TabIndex = 6;
			this.label3.Text = "OpCode";
			// 
			// txtLeopardSequence
			// 
			this.txtLeopardSequence.Location = new System.Drawing.Point(127, 58);
			this.txtLeopardSequence.Name = "txtLeopardSequence";
			this.txtLeopardSequence.Size = new System.Drawing.Size(150, 23);
			this.txtLeopardSequence.TabIndex = 5;
			// 
			// label2
			// 
			this.label2.AutoSize = true;
			this.label2.Location = new System.Drawing.Point(16, 61);
			this.label2.Name = "label2";
			this.label2.Size = new System.Drawing.Size(105, 15);
			this.label2.TabIndex = 4;
			this.label2.Text = "Leopard Sequence";
			// 
			// txtPabPortSerialNumber
			// 
			this.txtPabPortSerialNumber.Location = new System.Drawing.Point(127, 22);
			this.txtPabPortSerialNumber.Name = "txtPabPortSerialNumber";
			this.txtPabPortSerialNumber.Size = new System.Drawing.Size(150, 23);
			this.txtPabPortSerialNumber.TabIndex = 3;
			// 
			// label1
			// 
			this.label1.AutoSize = true;
			this.label1.Location = new System.Drawing.Point(6, 25);
			this.label1.Name = "label1";
			this.label1.Size = new System.Drawing.Size(115, 15);
			this.label1.TabIndex = 2;
			this.label1.Text = "PAB Port Serial No.";
			// 
			// btnBuildOpcode
			// 
			this.btnBuildOpcode.Location = new System.Drawing.Point(6, 96);
			this.btnBuildOpcode.Name = "btnBuildOpcode";
			this.btnBuildOpcode.Size = new System.Drawing.Size(740, 23);
			this.btnBuildOpcode.TabIndex = 1;
			this.btnBuildOpcode.Text = "Build Opcode Command";
			this.btnBuildOpcode.UseVisualStyleBackColor = true;
			this.btnBuildOpcode.Click += new System.EventHandler(this.btnBuildOpcode_Click);
			// 
			// txtOpcodeCommandHex
			// 
			this.txtOpcodeCommandHex.Location = new System.Drawing.Point(6, 125);
			this.txtOpcodeCommandHex.Multiline = true;
			this.txtOpcodeCommandHex.Name = "txtOpcodeCommandHex";
			this.txtOpcodeCommandHex.ScrollBars = ScrollBars.Vertical;
			this.txtOpcodeCommandHex.Size = new System.Drawing.Size(740, 120);
			this.txtOpcodeCommandHex.TabIndex = 0;
			// 
			// groupBox2
			// 
			this.groupBox2.Controls.Add(this.lblCrcValue);
			this.groupBox2.Controls.Add(this.txtCrcPacketHex);
			this.groupBox2.Controls.Add(this.btnBuildCrcPacket);
			this.groupBox2.Controls.Add(this.txtCommand);
			this.groupBox2.Controls.Add(this.label8);
			this.groupBox2.Controls.Add(this.txtId);
			this.groupBox2.Controls.Add(this.label7);
			this.groupBox2.Location = new System.Drawing.Point(12, 278);
			this.groupBox2.Name = "groupBox2";
			this.groupBox2.Size = new System.Drawing.Size(760, 200);
			this.groupBox2.TabIndex = 1;
			this.groupBox2.TabStop = false;
			this.groupBox2.Text = "Leopard CRC16 Packet";
			// 
			// lblCrcValue
			// 
			this.lblCrcValue.AutoSize = true;
			this.lblCrcValue.Location = new System.Drawing.Point(530, 25);
			this.lblCrcValue.Name = "lblCrcValue";
			this.lblCrcValue.Size = new System.Drawing.Size(124, 15);
			this.lblCrcValue.TabIndex = 6;
			this.lblCrcValue.Text = "CRC16 (big-endian): -";
			// 
			// txtCrcPacketHex
			// 
			this.txtCrcPacketHex.Location = new System.Drawing.Point(6, 96);
			this.txtCrcPacketHex.Multiline = true;
			this.txtCrcPacketHex.Name = "txtCrcPacketHex";
			this.txtCrcPacketHex.ScrollBars = ScrollBars.Vertical;
			this.txtCrcPacketHex.Size = new System.Drawing.Size(740, 98);
			this.txtCrcPacketHex.TabIndex = 5;
			// 
			// btnBuildCrcPacket
			// 
			this.btnBuildCrcPacket.Location = new System.Drawing.Point(6, 67);
			this.btnBuildCrcPacket.Name = "btnBuildCrcPacket";
			this.btnBuildCrcPacket.Size = new System.Drawing.Size(740, 23);
			this.btnBuildCrcPacket.TabIndex = 4;
			this.btnBuildCrcPacket.Text = "Build '0 ID CMD CRC CR' Packet";
			this.btnBuildCrcPacket.UseVisualStyleBackColor = true;
			this.btnBuildCrcPacket.Click += new System.EventHandler(this.btnBuildCrcPacket_Click);
			// 
			// txtCommand
			// 
			this.txtCommand.Location = new System.Drawing.Point(349, 22);
			this.txtCommand.Name = "txtCommand";
			this.txtCommand.Size = new System.Drawing.Size(160, 23);
			this.txtCommand.TabIndex = 3;
			// 
			// label8
			// 
			this.label8.AutoSize = true;
			this.label8.Location = new System.Drawing.Point(289, 25);
			this.label8.Name = "label8";
			this.label8.Size = new System.Drawing.Size(54, 15);
			this.label8.TabIndex = 2;
			this.label8.Text = "Command";
			// 
			// txtId
			// 
			this.txtId.Location = new System.Drawing.Point(123, 22);
			this.txtId.Name = "txtId";
			this.txtId.Size = new System.Drawing.Size(160, 23);
			this.txtId.TabIndex = 1;
			// 
			// label7
			// 
			this.label7.AutoSize = true;
			this.label7.Location = new System.Drawing.Point(16, 25);
			this.label7.Name = "label7";
			this.label7.Size = new System.Drawing.Size(101, 15);
			this.label7.TabIndex = 0;
			this.label7.Text = "ID (char or byte)";
			// 
			// MainForm
			// 
			this.AutoScaleDimensions = new System.Drawing.SizeF(7F, 15F);
			this.AutoScaleMode = AutoScaleMode.Font;
			this.ClientSize = new System.Drawing.Size(784, 491);
			this.Controls.Add(this.groupBox2);
			this.Controls.Add(this.groupBox1);
			this.Name = "MainForm";
			this.Text = "Leopard Command Tool";
			this.groupBox1.ResumeLayout(false);
			this.groupBox1.PerformLayout();
			this.groupBox2.ResumeLayout(false);
			this.groupBox2.PerformLayout();
			this.ResumeLayout(false);
		}

		private GroupBox groupBox1;
		private TextBox txtLeopardSequenceNumber;
		private Label label6;
		private TextBox txtTimestamp;
		private Label label5;
		private TextBox txtSequenceNumber;
		private Label label4;
		private TextBox txtOpCode;
		private Label label3;
		private TextBox txtLeopardSequence;
		private Label label2;
		private TextBox txtPabPortSerialNumber;
		private Label label1;
		private Button btnBuildOpcode;
		private TextBox txtOpcodeCommandHex;
		private GroupBox groupBox2;
		private Label lblCrcValue;
		private TextBox txtCrcPacketHex;
		private Button btnBuildCrcPacket;
		private TextBox txtCommand;
		private Label label8;
		private TextBox txtId;
		private Label label7;
	}
}


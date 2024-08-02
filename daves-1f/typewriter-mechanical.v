// IBM 1620 Logic Reproduction
// Bruce MacKinnon 7-July-2024
//
// Typewriter Control Mechanical Logic

module typewriter();

    // ===== Duo Relays =======================================================

    wire r4_pick_coil, r4_hold_coil;
    reg r4_state;
    wire r4_1no_sw = r4_state;
    wire r4_1nc_sw = !r4_1no_sw;
    wire r4_3no_sw = r4_state;
    wire r4_3nc_sw = !r4_3no_sw;
    wire r4_4no_sw = r4_state;
    wire r4_4nc_sw = !r4_4no_sw;
    always @ (r4_pick_coil, r4_hold_coil) begin
        r4_state <= (r4_pick_coil | r4_hold_coil);
    end

    wire r5_pick_coil, r5_hold_coil;
    reg r5_state;
    wire r5_1no_sw = r5_state;
    wire r5_1nc_sw = !r5_1no_sw;
    wire r5_3no_sw = r5_state;
    wire r5_3nc_sw = !r5_3no_sw;
    wire r5_4no_sw = r5_state;
    wire r5_4nc_sw = !r5_4no_sw;
    always @ (r5_pick_coil, r5_hold_coil) begin
        r5_state <= (r5_pick_coil | r5_hold_coil);
    end

    wire r6_pick_coil, r6_hold_coil;
    reg r6_state;
    wire r6_1no_sw = r6_state;
    wire r6_1nc_sw = !r6_1no_sw;
    wire r6_3no_sw = r6_state;
    wire r6_3nc_sw = !r6_3no_sw;
    wire r6_4no_sw = r6_state;
    wire r6_4nc_sw = !r6_4no_sw;
    always @ (r6_pick_coil, r6_hold_coil) begin
        r6_state <= (r6_pick_coil | r6_hold_coil);
    end

    wire r8_pick_coil, r8_hold_coil;
    reg r8_state;
    wire r8_1no_sw = r8_state;
    wire r8_1nc_sw = !r8_1no_sw;
    wire r8_2no_sw = r8_state;
    wire r8_2nc_sw = !r8_2no_sw;
    wire r8_3no_sw = r8_state;
    wire r8_3nc_sw = !r8_3no_sw;
    wire r8_4no_sw = r8_state;
    wire r8_4nc_sw = !r8_4no_sw;
    always @ (r8_pick_coil, r8_hold_coil) begin 
        r8_state <= (r8_pick_coil | r8_hold_coil);
    end

    wire r9_pick_coil, r9_hold_coil;
    reg r9_state;
    wire r9_1no_sw = r9_state;
    wire r9_1nc_sw = !r9_1no_sw;
    wire r9_2no_sw = r9_state;
    wire r9_2nc_sw = !r9_2no_sw;
    always @ (r9_pick_coil, r9_hold_coil) begin
        r9_state <= (r9_pick_coil | r9_hold_coil);
    end

    wire r11_pick_coil, r11_hold_coil;
    reg r11_state;
    wire r11_1no_sw = r11_state;
    wire r11_1nc_sw = !r11_1no_sw;
    wire r11_2no_sw = r11_state;
    wire r11_2nc_sw = !r11_2no_sw;
    always @ (r11_pick_coil, r11_hold_coil) begin
        r11_state <= (r11_pick_coil | r11_hold_coil);
    end

    wire r12_pick_coil, r12_hold_coil;
    reg r12_state;
    wire r12_1no_sw = r12_state;
    wire r12_1nc_sw = !r12_1no_sw;
    always @ (r12_pick_coil, r12_hold_coil) begin
        r12_state <= (r12_pick_coil | r12_hold_coil);
    end

    wire r15_pick_coil, r15_hold_coil;
    reg r15_state;
    wire r15_1no_sw = r15_state;
    wire r15_1nc_sw = !r15_1no_sw;
    wire r15_2no_sw = r15_state;
    wire r15_2nc_sw = !r15_2no_sw;
    always @ (r15_pick_coil, r15_hold_coil) begin
        r15_state <= (r15_pick_coil | r15_hold_coil);
    end 

    wire r16_pick_coil, r16_hold_coil;
    reg r16_state;
    wire r16_1no_sw = r16_state;
    wire r16_1nc_sw = !r16_1no_sw;
    wire r16_2no_sw = r16_state;
    wire r16_2nc_sw = !r16_2no_sw;
    wire r16_3no_sw = r16_state;
    wire r16_3nc_sw = !r16_3no_sw;
    always @ (r16_pick_coil, r16_hold_coil) begin 
        r16_state <= (r16_pick_coil | r16_hold_coil);
    end 

    wire r19_pick_coil, r19_hold_coil;
    reg r19_state;
    wire r19_1no_sw = r19_state;
    wire r19_1nc_sw = !r19_1no_sw;
    wire r19_2no_sw = r19_state;
    wire r19_2nc_sw = !r19_2no_sw;
    wire r19_3no_sw = r19_state;
    wire r19_3nc_sw = !r19_3no_sw;
    wire r19_4no_sw = r19_state;
    wire r19_4nc_sw = !r19_4no_sw;
    always @ (r19_pick_coil, r19_hold_coil) begin
        r19_state <= (r19_pick_coil | r19_hold_coil);
    end 

    wire r21_pick_coil, r21_hold_coil;
    reg r21_state;
    wire r21_1no_sw = r21_state;
    wire r21_1nc_sw = !r21_1no_sw;
    wire r21_2no_sw = r21_state;
    wire r21_2nc_sw = !r21_2no_sw;
    wire r21_3no_sw = r21_state;
    wire r21_3nc_sw = !r21_3no_sw;
    always @ (r21_pick_coil, r21_hold_coil) begin
        r21_state <= (r21_pick_coil | r21_hold_coil);
    end 

    wire r22_pick_coil, r22_hold_coil;
    reg r22_state;
    wire r22_1no_sw = r22_state;
    wire r22_1nc_sw = !r22_1no_sw;
    wire r22_2no_sw = r22_state;
    wire r22_2nc_sw = !r22_2no_sw;
    wire r22_3no_sw = r22_state;
    wire r22_3nc_sw = !r22_3no_sw;
    wire r22_4no_sw = r22_state;
    wire r22_4nc_sw = !r22_4no_sw;
    wire r22_5no_sw = r22_state;
    wire r22_5nc_sw = !r22_5no_sw;
    wire r22_6no_sw = r22_state;
    wire r22_6nc_sw = !r22_6no_sw;
    wire r22_7no_sw = r22_state;
    wire r22_7nc_sw = !r22_7no_sw;
    wire r22_8no_sw = r22_state;
    wire r22_8nc_sw = !r22_8no_sw;
    wire r22_9no_sw = r22_state;
    wire r22_9nc_sw = !r22_9no_sw;
    wire r22_10no_sw = r22_state;
    wire r22_10nc_sw = !r22_10no_sw;
    wire r22_11no_sw = r22_state;
    wire r22_11nc_sw = !r22_11no_sw;
    wire r22_12no_sw = r22_state;
    wire r22_12nc_sw = !r22_12no_sw;
    always @ (r22_pick_coil, r22_hold_coil) begin
        r22_state <= (r22_pick_coil | r22_hold_coil);
    end 

    wire r25_pick_coil, r25_hold_coil;
    reg r25_state;
    wire r25_1no_sw = r25_state;
    wire r25_1nc_sw = !r25_1no_sw;
    wire r25_2no_sw = r25_state;
    wire r25_2nc_sw = !r25_2no_sw;
    wire r25_3no_sw = r25_state;
    wire r25_3nc_sw = !r25_3no_sw;
    wire r25_9no_sw = r25_state;
    wire r25_9nc_sw = !r25_9no_sw;
    wire r25_10no_sw = r25_state;
    wire r25_10nc_sw = !r25_10no_sw;
    wire r25_11no_sw = r25_state;
    wire r25_11nc_sw = !r25_11no_sw;
    wire r25_12no_sw = r25_state;
    wire r25_12nc_sw = !r25_12no_sw;
    always @ (r25_pick_coil, r25_hold_coil) begin
        r25_state <= (r25_pick_coil | r25_hold_coil);
    end 

    wire r28_pick_coil, r28_hold_coil;
    reg r28_state;
    wire r28_1no_sw = r28_state;
    wire r28_1nc_sw = !r28_1no_sw;
    wire r28_2no_sw = r28_state;
    wire r28_2nc_sw = !r28_2no_sw;
    wire r28_3no_sw = r28_state;
    wire r28_3nc_sw = !r28_3no_sw;
    wire r28_4no_sw = r28_state;
    wire r28_4nc_sw = !r28_4no_sw;
    wire r28_5no_sw = r28_state;
    wire r28_5nc_sw = !r28_5no_sw;
    wire r28_6no_sw = r28_state;
    wire r28_6nc_sw = !r28_6no_sw;
    wire r28_7no_sw = r28_state;
    wire r28_7nc_sw = !r28_7no_sw;
    wire r28_8no_sw = r28_state;
    wire r28_8nc_sw = !r28_8no_sw;
    wire r28_9no_sw = r28_state;
    wire r28_9nc_sw = !r28_9no_sw;
    wire r28_10no_sw = r28_state;
    wire r28_10nc_sw = !r28_10no_sw;
    wire r28_11no_sw = r28_state;
    wire r28_11nc_sw = !r28_11no_sw;
    wire r28_12no_sw = r28_state;
    wire r28_12nc_sw = !r28_12no_sw;
    always @ (r28_pick_coil, r28_hold_coil) begin
        r28_state <= (r28_pick_coil | r28_hold_coil);
    end 

    wire r31_pick_coil, r31_hold_coil;
    reg r31_state;
    wire r31_1no_sw = r31_state;
    wire r31_1nc_sw = !r31_1no_sw;
    wire r31_2no_sw = r31_state;
    wire r31_2nc_sw = !r31_2no_sw;
    wire r31_3no_sw = r31_state;
    wire r31_3nc_sw = !r31_3no_sw;
    wire r31_4no_sw = r31_state;
    wire r31_4nc_sw = !r31_4no_sw;
    always @ (r31_pick_coil, r31_hold_coil) begin
        r31_state <= (r31_pick_coil | r31_hold_coil);
    end 

    wire r38_pick_coil, r38_hold_coil;
    reg r38_state;
    wire r38_1no_sw = r38_state;
    wire r38_1nc_sw = !r38_1no_sw;
    wire r38_2no_sw = r38_state;
    wire r38_2nc_sw = !r38_2no_sw;
    wire r38_3no_sw = r38_state;
    wire r38_3nc_sw = !r38_3no_sw;
    wire r38_4no_sw = r38_state;
    wire r38_4nc_sw = !r38_4no_sw;
    always @ (r38_pick_coil, r38_hold_coil) begin
        r38_state <= (r38_pick_coil | r38_hold_coil);
    end 
    
    wire r41_pick_coil, r41_hold_coil;
    reg r41_state;
    wire r41_1no_sw = r41_state;
    wire r41_1nc_sw = !r41_1no_sw;
    wire r41_2no_sw = r41_state;
    wire r41_2nc_sw = !r41_2no_sw;
    wire r41_3no_sw = r41_state;
    wire r41_3nc_sw = !r41_3no_sw;
    wire r41_4no_sw = r41_state;
    wire r41_4nc_sw = !r41_4no_sw;
    always @ (r41_pick_coil, r41_hold_coil) begin
        r41_state <= (r41_pick_coil | r41_hold_coil);
    end 

    wire r42_pick_coil, r42_hold_coil;
    reg r42_state;
    wire r42_1no_sw = r42_state;
    wire r42_1nc_sw = !r42_1no_sw;
    wire r42_2no_sw = r42_state;
    wire r42_2nc_sw = !r42_2no_sw;
    wire r42_3no_sw = r42_state;
    wire r42_3nc_sw = !r42_3no_sw;
    wire r42_4no_sw = r42_state;
    wire r42_4nc_sw = !r42_4no_sw;
    always @ (r42_pick_coil, r42_hold_coil) begin
        r42_state <= (r42_pick_coil | r42_hold_coil);
    end 

    wire r45_pick_coil, r45_hold_coil;
    reg r45_state;
    wire r45_1no_sw = r45_state;
    wire r45_1nc_sw = !r45_1no_sw;
    wire r45_2no_sw = r45_state;
    wire r45_2nc_sw = !r45_2no_sw;
    wire r45_3no_sw = r45_state;
    wire r45_3nc_sw = !r45_3no_sw;
    wire r45_4no_sw = r45_state;
    wire r45_4nc_sw = !r45_4no_sw;
    always @ (r45_pick_coil, r45_hold_coil) begin
        r45_state <= (r45_pick_coil | r45_hold_coil);
    end

    wire r46_pick_coil, r46_hold_coil;
    reg r46_state;
    wire r46_1no_sw = r46_state;
    wire r46_1nc_sw = !r46_1no_sw;
    wire r46_2no_sw = r46_state;
    wire r46_2nc_sw = !r46_2no_sw;
    wire r46_3no_sw = r46_state;
    wire r46_3nc_sw = !r46_3no_sw;
    wire r46_4no_sw = r46_state;
    wire r46_4nc_sw = !r46_4no_sw;
    always @ (r46_pick_coil, r46_hold_coil) begin
        r46_state <= (r46_pick_coil | r46_hold_coil);
    end

    wire r49_pick_coil, r49_hold_coil;
    reg r49_state;
    wire r49_1no_sw = r49_state;
    wire r49_1nc_sw = !r49_1no_sw;
    wire r49_2no_sw = r49_state;
    wire r49_2nc_sw = !r49_2no_sw;
    wire r49_3no_sw = r49_state;
    wire r49_3nc_sw = !r49_3no_sw;
    wire r49_4no_sw = r49_state;
    wire r49_4nc_sw = !r49_4no_sw;
    always @ (r49_pick_coil, r49_hold_coil) begin
        r49_state <= (r49_pick_coil | r49_hold_coil);
    end 

    wire r50_pick_coil, r50_hold_coil;
    reg r50_state;
    wire r50_1no_sw = r50_state;
    wire r50_1nc_sw = !r50_1no_sw;
    wire r50_2no_sw =  r50_state;
    wire r50_2nc_sw = !r50_2no_sw;
    wire r50_3no_sw =  r50_state;
    wire r50_3nc_sw = !r50_3no_sw;
    wire r50_4no_sw =  r50_state;
    wire r50_4nc_sw = !r50_4no_sw;
    wire r50_5no_sw =  r50_state;
    wire r50_5nc_sw = !r50_5no_sw;
    wire r50_6no_sw =  r50_state;
    wire r50_6nc_sw = !r50_6no_sw;
    wire r50_7no_sw =  r50_state;
    wire r50_7nc_sw = !r50_7no_sw;
    wire r50_8no_sw =  r50_state;
    wire r50_8nc_sw = !r50_8no_sw;
    wire r50_9no_sw =  r50_state;
    wire r50_9nc_sw = !r50_9no_sw;
    wire r50_10no_sw = r50_state;
    wire r50_10nc_sw = !r50_10no_sw;
    wire r50_11no_sw =  r50_state;
    wire r50_11nc_sw = !r50_11no_sw;
    wire r50_12no_sw =  r50_state;
    wire r50_12nc_sw = !r50_12no_sw;
    always @ (r50_pick_coil, r50_hold_coil) begin
        r50_state <= (r50_pick_coil | r50_hold_coil);
    end

    // ===== Latching Relays ===================================================

    wire r1_pick_coil, r1_trip_coil;
    reg r1_state = 1'b0;
    wire r1_1no_sw = r1_state;
    wire r1_1nc_sw = !r1_1no_sw;
    wire r1_2no_sw = r1_state;
    wire r1_2nc_sw = !r1_2no_sw;
    wire r1_3no_sw = r1_state;
    wire r1_3nc_sw = !r1_3no_sw;
    always @ (r1_pick_coil, r1_trip_coil) begin
        r1_state <= (r1_state & !r1_trip_coil) | r1_pick_coil;
    end 

    wire r3_pick_coil, r3_trip_coil;
    reg r3_state = 1'b0;
    wire r3_1no_sw = r3_state;
    wire r3_1nc_sw = !r3_1no_sw;
    wire r3_2no_sw = r3_state;
    wire r3_2nc_sw = !r3_2no_sw;
    wire r3_3no_sw = r3_state;
    wire r3_3nc_sw = !r3_3no_sw;
    wire r3_4no_sw = r3_state;
    wire r3_4nc_sw = !r3_4no_sw;
    always @ (r3_pick_coil, r3_trip_coil) begin
        r3_state <= (r3_state & !r3_trip_coil) | r3_pick_coil;
    end 

    // FLAG INTLK
    wire r7_pick_coil, r7_trip_coil;
    reg r7_state = 1'b0;
    wire r7_1no_sw = r7_state;
    wire r7_1nc_sw = !r7_1no_sw;
    wire r7_2no_sw = r7_state;
    wire r7_2nc_sw = !r7_2no_sw;
    wire r7_3no_sw = r7_state;
    wire r7_3nc_sw = !r7_3no_sw;
    wire r7_4no_sw = r7_state;
    wire r7_4nc_sw = !r7_4no_sw;
    always @ (r7_pick_coil, r7_trip_coil) begin
        r7_state <= (r7_state & !r7_trip_coil) | r7_pick_coil;
    end 

    // SHIFT
    wire r10_pick_coil, r10_trip_coil;
    reg r10_state = 1'b0;
    wire r10_1no_sw = r10_state;
    wire r10_1nc_sw = !r10_1no_sw;
    always @ (r10_pick_coil, r10_trip_coil) begin
        r10_state <= (r10_state & !r10_trip_coil) | r10_pick_coil;
    end 

    // TEST
    wire r20_pick_coil, r20_trip_coil;
    reg r20_state = 1'b0;
    wire r20_1no_sw = r20_state;
    wire r20_1nc_sw = !r20_1no_sw;
    wire r20_2no_sw = r20_state;
    wire r20_2nc_sw = !r20_2no_sw;
    wire r20_3no_sw = r20_state;
    wire r20_3nc_sw = !r20_3no_sw;
    wire r20_4no_sw = r20_state;
    wire r20_4nc_sw = !r20_4no_sw;
    always @ (r20_pick_coil, r20_trip_coil) begin
        r20_state <= (r20_state & !r20_trip_coil) | r20_pick_coil;
    end 

    wire r39_pick_coil, r39_trip_coil;
    reg r39_state = 1'b0;
    wire r39_1no_sw = r39_state;
    wire r39_1nc_sw = !r39_1no_sw;
    wire r39_2no_sw = r39_state;
    wire r39_2nc_sw = !r39_2no_sw;
    wire r39_3no_sw = r39_state;
    wire r39_3nc_sw = !r39_3no_sw;
    always @ (r39_pick_coil, r39_trip_coil) begin
        r39_state <= (r39_state & !r39_trip_coil) | r39_pick_coil;
    end 

    wire r40_pick_coil, r40_trip_coil;
    reg r40_state = 1'b0;
    wire r40_1no_sw = r40_state;
    wire r40_1nc_sw = !r40_1no_sw;
    wire r40_2no_sw = r40_state;
    wire r40_2nc_sw = !r40_2no_sw;
    always @ (r40_pick_coil, r40_trip_coil) begin
        r40_state <= (r40_state & !r40_trip_coil) | r40_pick_coil;
    end 

    wire r54_pick_coil, r54_trip_coil;
    reg r54_state = 1'b0;
    wire r54_1no_sw = r54_state;
    wire r54_1nc_sw = !r54_1no_sw;
    wire r54_2no_sw = r54_state;
    wire r54_2nc_sw = !r54_2no_sw;
    wire r54_3no_sw = r54_state;
    wire r54_3nc_sw = !r54_3no_sw;
    wire r54_4no_sw = r54_state;
    wire r54_4nc_sw = !r54_4no_sw;
    always @ (r54_pick_coil, r54_trip_coil) begin
        r54_state <= (r54_state & !r54_trip_coil) | r54_pick_coil;
    end 

    // ===== CRCB Cam Relay ======================================================

    integer _angle;
    integer _cycle;
    wire crcb_1no_sw = (_angle >= 0) & (_angle < 51);
    wire crcb_2no_sw = (_angle >= 50) & (_angle < 100);
    wire crcb_3no_sw = (_angle >= 99) & (_angle < 309);
    wire crcb_4no_sw = (_angle >= 171) & (_angle < 221);
    wire crcb_5no_sw = (_angle >= 220) & (_angle < 300);
    wire crcb_6no_sw = (_angle >= 310) & (_angle < 360);

    // ===== Other Connections ====================================================

    //tab_intlk_contact_no = 
    //carr_rtn_intlk_contact_no = 
    //last_col_contact_no = 

    wire ps_shift_sol;
    wire sw_shiftcontact_no_sw = ps_shift_sol;

    // Solenoids
    wire ps_a_sol;
    wire ps_b_sol;
    wire ps_c_sol;
    wire ps_d_sol;
    wire ps_e_sol;
    wire ps_f_sol;
    wire ps_g_sol;
    wire ps_h_sol;
    wire ps_n_sol;
    wire ps_p_sol;
    wire ps_q_sol;
    wire ps_r_sol;
    wire ps_s_sol;
    wire ps_t_sol;
    wire ps_v_sol;
    wire ps_w_sol;
    wire ps_x_sol;
    wire ps_y_sol;
    wire ps_z_sol;
    wire ps_0_sol;
    wire ps_1u_sol;
    wire ps_2i_sol;
    wire ps_3o_sol;
    wire ps_4j_sol;
    wire ps_5k_sol;
    wire ps_6l_sol;
    wire ps_7m_sol;
    wire ps_8comma_sol;
    wire ps_9period_sol;
    wire ps_space_sol;
    wire ps_at_sol;
    wire ps_dash_sol;
    wire ps_slash_sol;
    wire ps_plus_sol;
    wire ps_star_sol;
    wire ps_lparen_sol;
    wire ps_rparen_sol;
    wire ps_dollar_sol;
    wire ps_ne_sol;
    wire ps_overscore_sol;
    wire ps_centerscore_sol;
    wire ps_invalidchar_sol;
    wire ps_tab_sol;
    wire ps_carr_rtn_sol;
    wire ps_keylock_sol;

    // ===== Temporary Logic =======================================================

    // ----- Page 01.82.60.1 -------------------------------------------------------

    // Positive logic.  A logic HI on the input turns the switch on (i.e. path 
    // to ground is completed).
    wire switch_wr_status_dr_no_sw = 1;
    wire switch_not_wr_status_dr_no_sw = 0;

    // ----- Page 01.82.62.1 -------------------------------------------------------

    wire negs_op_36_rn = 1;
    wire negs_op_38_wn = 0;
    wire negs_op_35_dn_p = 1;
    wire s_not_wr_num_intlk = 0;
    
    // CD at 3E
    wire sms_01da_1d07_d = !(negs_op_36_rn & negs_op_38_wn & negs_op_35_dn_p);

    // MX at 4F
    wire sms_01da_1d06_k = !sms_01da_1d07_d;
    
    // Positive logic.  A logic HI on the input turns the switch on (i.e. path 
    // to ground is completed).
    wire switch_wr_num_status_dr_no_sw = sms_01da_1d07_d;
    wire switch_not_wr_num_status_dr_no_sw = sms_01da_1d06_k;

endmodule
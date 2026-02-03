```mermaid
graph LR
    cb0((Callback 0))
    n0["url<br/>.pathname"] --> cb0
    cb0 --> n1["navbar-container<br/>.children"]
    cb0 --> n2["page-content<br/>.children"]
    cb1((Callback 1))
    n3["bpmn-svg-store (['MATCH'])<br/>.data"] --> cb1
    n4["bpmn-svg-zoom-slider (['MATCH'])<br/>.value"] --> cb1
    n5["bpmn-svg-reset-zoom (['MATCH'])<br/>.n_clicks"] --> cb1
    n6["bpmn-svg-increase-zoom (['MATCH'])<br/>.n_clicks"] --> cb1
    n7["bpmn-svg-decrease-zoom (['MATCH'])<br/>.n_clicks"] --> cb1
    n8["bpmn-svg-zoom-settings (['MATCH'])<br/>.data"] -.-> cb1
    cb1 --> n9["bpmn-svg-svg (['MATCH'])<br/>.children"]
    cb1 --> n4["bpmn-svg-zoom-slider (['MATCH'])<br/>.value"]
    cb2((Callback 2))
    n10["petri-svg-store (['MATCH'])<br/>.data"] --> cb2
    n11["petri-svg-zoom-slider (['MATCH'])<br/>.value"] --> cb2
    n12["petri-svg-reset-zoom (['MATCH'])<br/>.n_clicks"] --> cb2
    n13["petri-svg-increase-zoom (['MATCH'])<br/>.n_clicks"] --> cb2
    n14["petri-svg-decrease-zoom (['MATCH'])<br/>.n_clicks"] --> cb2
    n15["petri-svg-zoom-settings (['MATCH'])<br/>.data"] -.-> cb2
    cb2 --> n16["petri-svg-svg (['MATCH'])<br/>.children"]
    cb2 --> n11["petri-svg-zoom-slider (['MATCH'])<br/>.value"]
    cb3((Callback 3))
    n17["bdd-store (['MATCH'])<br/>.data"] --> cb3
    n18["bdd-zoom-slider (['MATCH'])<br/>.value"] --> cb3
    n19["bdd-reset-zoom (['MATCH'])<br/>.n_clicks"] --> cb3
    n20["bdd-increase-zoom (['MATCH'])<br/>.n_clicks"] --> cb3
    n21["bdd-decrease-zoom (['MATCH'])<br/>.n_clicks"] --> cb3
    n22["bdd-zoom-settings (['MATCH'])<br/>.data"] -.-> cb3
    cb3 --> n23["bdd-svg (['MATCH'])<br/>.children"]
    cb3 --> n18["bdd-zoom-slider (['MATCH'])<br/>.value"]
    cb4((Callback 4))
    n24["ALL (['ALL'])<br/>.value"] --> cb4
    n24["ALL (['ALL'])<br/>.id"] -.-> cb4
    n25["bpmn-store<br/>.data"] -.-> cb4
    cb4 --> n25["bpmn-store<br/>.data"]
    cb4 --> n26["bpmn-svg-store (main)<br/>.data"]
    cb4 --> n27["bpmn-alert<br/>.children"]
    cb5((Callback 5))
    n28["min-duration (['ALL'])<br/>.value"] --> cb5
    n29["max-duration (['ALL'])<br/>.value"] --> cb5
    n28["min-duration (['ALL'])<br/>.id"] -.-> cb5
    n25["bpmn-store<br/>.data"] -.-> cb5
    cb5 --> n25["bpmn-store<br/>.data"]
    cb5 --> n26["bpmn-svg-store (main)<br/>.data"]
    cb5 --> n27["bpmn-alert<br/>.children"]
    cb6((Callback 6))
    n30["add-impact-button<br/>.n_clicks"] --> cb6
    n31["new-impact-name<br/>.value"] -.-> cb6
    n25["bpmn-store<br/>.data"] -.-> cb6
    n32["bound-store<br/>.data"] -.-> cb6
    cb6 --> n25["bpmn-store<br/>.data"]
    cb6 --> n26["bpmn-svg-store (main)<br/>.data"]
    cb6 --> n32["bound-store<br/>.data"]
    cb6 --> n27["bpmn-alert<br/>.children"]
    cb6 --> n33["task-impacts-table<br/>.children"]
    cb7((Callback 7))
    n34["remove-impact (['ALL'])<br/>.n_clicks"] --> cb7
    n25["bpmn-store<br/>.data"] -.-> cb7
    n32["bound-store<br/>.data"] -.-> cb7
    n34["remove-impact (['ALL'])<br/>.id"] -.-> cb7
    cb7 --> n25["bpmn-store<br/>.data"]
    cb7 --> n26["bpmn-svg-store (main)<br/>.data"]
    cb7 --> n32["bound-store<br/>.data"]
    cb7 --> n27["bpmn-alert<br/>.children"]
    cb7 --> n33["task-impacts-table<br/>.children"]
    cb8((Callback 8))
    n35["choice-delay (['ALL'])<br/>.value"] --> cb8
    n35["choice-delay (['ALL'])<br/>.id"] -.-> cb8
    n25["bpmn-store<br/>.data"] -.-> cb8
    cb8 --> n25["bpmn-store<br/>.data"]
    cb8 --> n26["bpmn-svg-store (main)<br/>.data"]
    cb8 --> n27["bpmn-alert<br/>.children"]
    cb9((Callback 9))
    n36["nature-prob (['ALL'])<br/>.value"] --> cb9
    n36["nature-prob (['ALL'])<br/>.id"] -.-> cb9
    n25["bpmn-store<br/>.data"] -.-> cb9
    cb9 --> n25["bpmn-store<br/>.data"]
    cb9 --> n26["bpmn-svg-store (main)<br/>.data"]
    cb9 --> n27["bpmn-alert<br/>.children"]
    cb10((Callback 10))
    n37["loop-prob (['ALL'])<br/>.value"] --> cb10
    n38["loop-round (['ALL'])<br/>.value"] --> cb10
    n37["loop-prob (['ALL'])<br/>.id"] -.-> cb10
    n25["bpmn-store<br/>.data"] -.-> cb10
    cb10 --> n25["bpmn-store<br/>.data"]
    cb10 --> n26["bpmn-svg-store (main)<br/>.data"]
    cb10 --> n27["bpmn-alert<br/>.children"]
    cb11((Callback 11))
    n39["expression-bpmn<br/>.value"] --> cb11
    n25["bpmn-store<br/>.data"] -.-> cb11
    n32["bound-store<br/>.data"] -.-> cb11
    cb11 --> n25["bpmn-store<br/>.data"]
    cb11 --> n26["bpmn-svg-store (main)<br/>.data"]
    cb11 --> n40["petri-svg-store (main)<br/>.data"]
    cb11 --> n41["simulation-store<br/>.data"]
    cb11 --> n32["bound-store<br/>.data"]
    cb11 --> n27["bpmn-alert<br/>.children"]
    cb11 --> n33["task-impacts-table<br/>.children"]
    cb11 --> n42["task-durations-table<br/>.children"]
    cb11 --> n43["choice-table<br/>.children"]
    cb11 --> n44["nature-table<br/>.children"]
    cb11 --> n45["loop-table<br/>.children"]
    cb12((Callback 12))
    n25["bpmn-store<br/>.data"] --> cb12
    n39["expression-bpmn<br/>.value"] -.-> cb12
    cb12 --> n39["expression-bpmn<br/>.value"]
    cb13((Callback 13))
    n32["bound-store<br/>.data"] --> cb13
    n25["bpmn-store<br/>.data"] -.-> cb13
    cb13 --> n46["bound-table<br/>.children"]
    cb14((Callback 14))
    n47["bound-input (['ALL'])<br/>.value"] --> cb14
    n47["bound-input (['ALL'])<br/>.id"] -.-> cb14
    n32["bound-store<br/>.data"] -.-> cb14
    cb14 --> n32["bound-store<br/>.data"]
    cb15((Callback 15))
    n48["selected_bound (['ALL'])<br/>.n_clicks"] --> cb15
    n48["selected_bound (['ALL'])<br/>.value"] -.-> cb15
    n32["bound-store<br/>.data"] -.-> cb15
    n25["bpmn-store<br/>.data"] -.-> cb15
    cb15 --> n32["bound-store<br/>.data"]
    cb16((Callback 16))
    n49["selected_bound (['ALL'])<br/>.n_clicks"] --> cb16
    n49["selected_bound (['ALL'])<br/>.value"] -.-> cb16
    n32["bound-store<br/>.data"] -.-> cb16
    n25["bpmn-store<br/>.data"] -.-> cb16
    cb16 --> n32["bound-store<br/>.data"]
    cb17((Callback 17))
    n50["sort-header (['ALL'])<br/>.n_clicks"] --> cb17
    n51["sort_store_guaranteed<br/>.data"] -.-> cb17
    n25["bpmn-store<br/>.data"] -.-> cb17
    cb17 --> n52["guaranteed-table<br/>.children"]
    cb17 --> n51["sort_store_guaranteed<br/>.data"]
    cb18((Callback 18))
    n53["sort-header (['ALL'])<br/>.n_clicks"] --> cb18
    n54["sort_store_possible_min<br/>.data"] -.-> cb18
    n25["bpmn-store<br/>.data"] -.-> cb18
    cb18 --> n55["possible_min-table<br/>.children"]
    cb18 --> n54["sort_store_possible_min<br/>.data"]
    cb19((Callback 19))
    n56["find-strategy-button<br/>.n_clicks"] --> cb19
    n25["bpmn-store<br/>.data"] -.-> cb19
    n32["bound-store<br/>.data"] -.-> cb19
    cb19 --> n57["strategy_output<br/>.children"]
    cb19 --> n51["sort_store_guaranteed<br/>.data"]
    cb19 --> n54["sort_store_possible_min<br/>.data"]
    cb19 --> n58["strategy-alert<br/>.children"]
    cb20((Callback 20))
    n59["toggle-sidebar<br/>.n_clicks"] --> cb20
    n60["sidebar-visible<br/>.data"] -.-> cb20
    n61["sidebar-width<br/>.data"] -.-> cb20
    n62["split-pane<br/>.size"] -.-> cb20
    cb20 --> n60["sidebar-visible<br/>.data"]
    cb20 --> n61["sidebar-width<br/>.data"]
    cb21((Callback 21))
    n60["sidebar-visible<br/>.data"] --> cb21
    n61["sidebar-width<br/>.data"] -.-> cb21
    cb21 --> n62["split-pane<br/>.size"]
    cb22((Callback 22))
    n63["chat-clear-btn<br/>.n_clicks"] --> cb22
    cb22 --> n64["chat-history<br/>.data"]
    cb22 --> n65["pending-message<br/>.data"]
    cb22 --> n66["reset-trigger<br/>.data"]
    cb23((Callback 23))
    n66["reset-trigger<br/>.data"] --> cb23
    cb23 --> n66["reset-trigger<br/>.data"]
    cb24((Callback 24))
    n65["pending-message<br/>.data"] --> cb24
    n66["reset-trigger<br/>.data"] --> cb24
    cb24 --> n67["chat-send-btn<br/>.disabled"]
    cb24 --> n68["chat-send-btn<br/>.style"]
    cb24 --> n69["chat-clear-btn<br/>.disabled"]
    cb24 --> n70["chat-clear-btn<br/>.style"]
    cb24 --> n71["llm-provider<br/>.disabled"]
    cb24 --> n72["llm-model<br/>.disabled"]
    cb24 --> n73["llm-api-key<br/>.disabled"]
    cb24 --> n74["llm-model-custom<br/>.disabled"]
    cb25((Callback 25))
    n75["chat-output<br/>.children"] --> cb25
    cb25 --> n76["dummy-output<br/>.children"]
    cb26((Callback 26))
    n77["llm-provider<br/>.value"] --> cb26
    n78["llm-model<br/>.value"] -.-> cb26
    cb26 --> n79["llm-model<br/>.options"]
    cb26 --> n78["llm-model<br/>.value"]
    cb26 --> n80["llm-api-key-container<br/>.style"]
    cb27((Callback 27))
    n81["chat-send-btn<br/>.n_clicks"] --> cb27
    n82["chat-input<br/>.value"] -.-> cb27
    n64["chat-history<br/>.data"] -.-> cb27
    cb27 --> n64["chat-history<br/>.data"]
    cb27 --> n65["pending-message<br/>.data"]
    cb27 --> n82["chat-input<br/>.value"]
    cb28((Callback 28))
    n65["pending-message<br/>.data"] --> cb28
    n64["chat-history<br/>.data"] -.-> cb28
    n25["bpmn-store<br/>.data"] -.-> cb28
    n32["bound-store<br/>.data"] -.-> cb28
    n77["llm-provider<br/>.value"] -.-> cb28
    n78["llm-model<br/>.value"] -.-> cb28
    n83["llm-model-custom<br/>.value"] -.-> cb28
    n84["llm-api-key<br/>.value"] -.-> cb28
    cb28 --> n64["chat-history<br/>.data"]
    cb28 --> n65["pending-message<br/>.data"]
    cb28 --> n25["bpmn-store<br/>.data"]
    cb28 --> n32["bound-store<br/>.data"]
    cb28 --> n26["bpmn-svg-store (main)<br/>.data"]
    cb28 --> n33["task-impacts-table<br/>.children"]
    cb28 --> n42["task-durations-table<br/>.children"]
    cb28 --> n43["choice-table<br/>.children"]
    cb28 --> n44["nature-table<br/>.children"]
    cb28 --> n45["loop-table<br/>.children"]
    cb29((Callback 29))
    n64["chat-history<br/>.data"] --> cb29
    cb29 --> n75["chat-output<br/>.children"]
    cb30((Callback 30))
    n85["upload-data<br/>.contents"] --> cb30
    n86["upload-data<br/>.filename"] -.-> cb30
    n32["bound-store<br/>.data"] -.-> cb30
    cb30 --> n25["bpmn-store<br/>.data"]
    cb30 --> n32["bound-store<br/>.data"]
    cb30 --> n26["bpmn-svg-store (main)<br/>.data"]
    cb30 --> n40["petri-svg-store (main)<br/>.data"]
    cb30 --> n41["simulation-store<br/>.data"]
    cb30 --> n33["task-impacts-table<br/>.children"]
    cb30 --> n42["task-durations-table<br/>.children"]
    cb30 --> n43["choice-table<br/>.children"]
    cb30 --> n44["nature-table<br/>.children"]
    cb30 --> n45["loop-table<br/>.children"]
    cb30 --> n39["expression-bpmn<br/>.value"]
    cb30 --> n27["bpmn-alert<br/>.children"]
    cb31((Callback 31))
    n87["download-bpmn-btn<br/>.n_clicks"] --> cb31
    n25["bpmn-store<br/>.data"] -.-> cb31
    cb31 --> n88["download-bpmn<br/>.data"]
    cb32((Callback 32))
    n0["url<br/>.search"] --> cb32
    n32["bound-store<br/>.data"] -.-> cb32
    cb32 --> n25["bpmn-store<br/>.data"]
    cb32 --> n32["bound-store<br/>.data"]
    cb32 --> n26["bpmn-svg-store (main)<br/>.data"]
    cb32 --> n33["task-impacts-table<br/>.children"]
    cb32 --> n42["task-durations-table<br/>.children"]
    cb32 --> n43["choice-table<br/>.children"]
    cb32 --> n44["nature-table<br/>.children"]
    cb32 --> n45["loop-table<br/>.children"]
    cb32 --> n39["expression-bpmn<br/>.value"]
    cb32 --> n27["bpmn-alert<br/>.children"]
    cb33((Callback 33))
    n41["simulation-store<br/>.data"] --> cb33
    cb33 --> n89["pending-decisions-body<br/>.children"]
    cb33 --> n90["pending-decisions-card-container<br/>.style"]
    cb34((Callback 34))
    n91["random-button (['ALL'])<br/>.n_clicks"] --> cb34
    n92["global-random<br/>.n_clicks"] --> cb34
    n93["gateway (['ALL'])<br/>.id"] -.-> cb34
    n41["simulation-store<br/>.data"] -.-> cb34
    cb34 --> n93["gateway (['ALL'])<br/>.value"]
    cb35((Callback 35))
    n41["simulation-store<br/>.data"] --> cb35
    n25["bpmn-store<br/>.data"] -.-> cb35
    cb35 --> n94["status-info-content<br/>.children"]
    cb35 --> n95["task-status-content<br/>.children"]
    cb36((Callback 36))
    n25["bpmn-store<br/>.data"] --> cb36
    cb36 --> n96["btn-back<br/>.disabled"]
    cb36 --> n97["btn-forward<br/>.disabled"]
    cb37((Callback 37))
    n25["bpmn-store<br/>.data"] --> cb37
    n41["simulation-store<br/>.data"] -.-> cb37
    n32["bound-store<br/>.data"] -.-> cb37
    cb37 --> n41["simulation-store<br/>.data"]
    cb38((Callback 38))
    n98["btn-back<br/>.n_clicks"] --> cb38
    n99["btn-forward<br/>.n_clicks"] --> cb38
    n25["bpmn-store<br/>.data"] -.-> cb38
    n93["gateway (['ALL'])<br/>.value"] -.-> cb38
    n41["simulation-store<br/>.data"] -.-> cb38
    n26["bpmn-svg-store (main)<br/>.data"] -.-> cb38
    n40["petri-svg-store (main)<br/>.data"] -.-> cb38
    n100["time-input<br/>.value"] -.-> cb38
    n32["bound-store<br/>.data"] -.-> cb38
    cb38 --> n41["simulation-store<br/>.data"]
    cb38 --> n26["bpmn-svg-store (main)<br/>.data"]
    cb38 --> n40["petri-svg-store (main)<br/>.data"]
    cb39((Callback 39))
    n101["view-mode<br/>.data"] --> cb39
    n25["bpmn-store<br/>.data"] -.-> cb39
    cb39 --> n102["petri-svg-store (main)<br/>.data"]
    cb40((Callback 40))
    n103["view-toggle-btn<br/>.n_clicks"] --> cb40
    n101["view-mode<br/>.data"] -.-> cb40
    cb40 --> n101["view-mode<br/>.data"]
    cb40 --> n104["view-toggle-btn<br/>.children"]
    cb41((Callback 41))
    n101["view-mode<br/>.data"] --> cb41
    cb41 --> n105["bpmn-container<br/>.style"]
    cb41 --> n106["petri-container<br/>.style"]
    cb42((Callback 42))
    n107["bpmn-example-svg-store (['MATCH'])<br/>.data"] --> cb42
    n108["bpmn-example-svg-zoom-slider (['MATCH'])<br/>.value"] --> cb42
    n109["bpmn-example-svg-reset-zoom (['MATCH'])<br/>.n_clicks"] --> cb42
    n110["bpmn-example-svg-increase-zoom (['MATCH'])<br/>.n_clicks"] --> cb42
    n111["bpmn-example-svg-decrease-zoom (['MATCH'])<br/>.n_clicks"] --> cb42
    n112["bpmn-example-svg-zoom-settings (['MATCH'])<br/>.data"] -.-> cb42
    cb42 --> n113["bpmn-example-svg-svg (['MATCH'])<br/>.children"]
    cb42 --> n108["bpmn-example-svg-zoom-slider (['MATCH'])<br/>.value"]
    cb43((Callback 43))
    n114["bpmn-example-download-btn<br/>.n_clicks"] --> cb43
    cb43 --> n115["bpmn-example-download<br/>.data"]
    cb44((Callback 44))
    n116["bpmn-example2-svg-store (['MATCH'])<br/>.data"] --> cb44
    n117["bpmn-example2-svg-zoom-slider (['MATCH'])<br/>.value"] --> cb44
    n118["bpmn-example2-svg-reset-zoom (['MATCH'])<br/>.n_clicks"] --> cb44
    n119["bpmn-example2-svg-increase-zoom (['MATCH'])<br/>.n_clicks"] --> cb44
    n120["bpmn-example2-svg-decrease-zoom (['MATCH'])<br/>.n_clicks"] --> cb44
    n121["bpmn-example2-svg-zoom-settings (['MATCH'])<br/>.data"] -.-> cb44
    cb44 --> n122["bpmn-example2-svg-svg (['MATCH'])<br/>.children"]
    cb44 --> n117["bpmn-example2-svg-zoom-slider (['MATCH'])<br/>.value"]
    cb45((Callback 45))
    n123["bpmn-example2-download-btn<br/>.n_clicks"] --> cb45
    cb45 --> n124["bpmn-example2-download<br/>.data"]
    cb46((Callback 46))
    n125["bpmn-example3-svg-store (['MATCH'])<br/>.data"] --> cb46
    n126["bpmn-example3-svg-zoom-slider (['MATCH'])<br/>.value"] --> cb46
    n127["bpmn-example3-svg-reset-zoom (['MATCH'])<br/>.n_clicks"] --> cb46
    n128["bpmn-example3-svg-increase-zoom (['MATCH'])<br/>.n_clicks"] --> cb46
    n129["bpmn-example3-svg-decrease-zoom (['MATCH'])<br/>.n_clicks"] --> cb46
    n130["bpmn-example3-svg-zoom-settings (['MATCH'])<br/>.data"] -.-> cb46
    cb46 --> n131["bpmn-example3-svg-svg (['MATCH'])<br/>.children"]
    cb46 --> n126["bpmn-example3-svg-zoom-slider (['MATCH'])<br/>.value"]
    cb47((Callback 47))
    n132["bpmn-example3-download-btn<br/>.n_clicks"] --> cb47
    cb47 --> n133["bpmn-example3-download<br/>.data"]
    cb48((Callback 48))
    n134["bpmn-example4-svg-store (['MATCH'])<br/>.data"] --> cb48
    n135["bpmn-example4-svg-zoom-slider (['MATCH'])<br/>.value"] --> cb48
    n136["bpmn-example4-svg-reset-zoom (['MATCH'])<br/>.n_clicks"] --> cb48
    n137["bpmn-example4-svg-increase-zoom (['MATCH'])<br/>.n_clicks"] --> cb48
    n138["bpmn-example4-svg-decrease-zoom (['MATCH'])<br/>.n_clicks"] --> cb48
    n139["bpmn-example4-svg-zoom-settings (['MATCH'])<br/>.data"] -.-> cb48
    cb48 --> n140["bpmn-example4-svg-svg (['MATCH'])<br/>.children"]
    cb48 --> n135["bpmn-example4-svg-zoom-slider (['MATCH'])<br/>.value"]
    cb49((Callback 49))
    n141["bpmn-example4-download-btn<br/>.n_clicks"] --> cb49
    cb49 --> n142["bpmn-example4-download<br/>.data"]
```

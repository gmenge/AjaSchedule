import json
import os

LOCALES = {
    "pt_BR": {
        # Seleção IP Matriz
        "ip_title": "AjaSchedule - Configuração de IP",
        "ip_instruction": "Informe o IP do servidor da Matriz:",
        "btn_save_continue": "Salvar e Continuar",
        "ip_warning_empty": "O IP não pode ficar em branco!",
        "warning_title": "Aviso",

        # Validação e Alteração de IP
        "lbl_source_single": "Origem",
        "lbl_destination_single": "Destino",
        "title_edit_selected": "EDITAR SELEÇÃO - {type} [{num:02d}]",
        "msg_select_item_edit_type": "Por favor, selecione um agendamento na lista para editar.",
        "msg_invalid_ip_title": "IP Inválido",
        "msg_invalid_ip_text": "O endereço IP informado é inválido. Por favor, verifique e tente novamente.",
        "msg_ip_updated_success": "Endereço IP da Matriz atualizado com sucesso!",
        "msg_success_title": "Sucesso",
        "lbl_current_ip": "IP Atual:",
        "log_ip_changed": "IP da Matriz alterado para {new}",

        # Rótulos Padrão de Fábrica (Entradas / Saídas)
        "default_input_label": "Origem {num}",
        "default_output_label": "Destino {num}",

        # Logs do Sistema e Conexão
        "log_initialized": "Sistema inicializado.",
        "log_conn_failed": "Falha ao conectar com a Matriz no IP {ip}.",
        "log_init_app": "Sistema inicializado e pronto.",
        "log_init_testing_conn": "Testando conexão com a Matriz no IP {ip}...",
        "log_init_conn_success": "Conectado com sucesso à Matriz ({ip}).",
        "log_init_conn_status": "Resposta da Matriz ({ip}): Status HTTP {status}.",
        "log_init_conn_timeout": "Tempo limite de conexão esgotado no IP {ip}.",
        "log_init_conn_failed": "Falha de rede ao conectar na Matriz no IP {ip}.",
        "log_save_agendamentos_failed": "Falha ao salvar agendamentos.",
        "log_status_check_failed": "Falha ao consultar estado do Destino [{dest}].",
        "log_conn_unreachable": "Matriz no IP {ip} está inacessível na rede.",
        "log_time_at": "às",
        
        # Logs de Ações de Agendamento
        "err_http_switch": "Erro HTTP {code} ao comutar Destino [{dest:02d}].",
        "err_connection_switch": "Falha ao comutar: Matriz no IP {ip} inacessível.",
        "log_routine_updated": "Rotina atualizada: Destino [{dest_new}] <- Origem [{src_new}] {time_at} {time_new}",
        "log_routine_added": "Rotina criada: Destino [{dest}] <- Origem [{src}] {time_at} {time}",
        "log_routine_deleted": "Rotina removida: Destino [{dest}]",
        "log_routine_removed": "Rotina removida: Destino [{dest}] <- Origem [{src}]",
        "log_single_event_removed": "Evento removido: Destino [{dest}] <- Origem [{src}]",
        "log_routine_executed": "Comutação executada com sucesso: Destino [{dest}] <- Origem [{src}]",
        
        # Interface Geral e Alertas
        "lbl_event_date": "Data do Evento (AAAA-MM-DD):",
        "msg_select_item_title": "Atenção",
        "msg_select_item_edit": "Por favor, selecione um agendamento na lista para editar.",
        "msg_select_item_delete": "Por favor, selecione um agendamento na lista para excluir.",
        "msg_select_item_run": "Por favor, selecione um agendamento na lista para executar.",
        "msg_confirm_delete_title": "Confirmar Exclusão",
        "msg_confirm_delete_text": "Tem certeza que deseja excluir o agendamento selecionado?",
        "app_title": "Agendador KUMO 64x64",
        "btn_cancel": "CANCELAR",
        "btn_confirm": "CONFIRMAR",
        "btn_save": "SALVAR",
        
        # Abas
        "tab_schedule": "Agendar Trocas",
        "tab_monitor": "Monitoramento em Tempo Real",
        "tab_logs": "Logs do Sistema",
        "tab_config": "Configurações",
        
        # Formulário de Agendamento
        "frame_new_schedule": "NOVO AGENDAMENTO DE ROTINA",
        "lbl_destination": "Destino:",
        "lbl_source": "Origem:",
        "lbl_frequency": "Frequência:",
        "lbl_time": "Horário:",
        "btn_now": "AGORA",
        "btn_add_schedule_action": "+ AGENDAR",
        "unit_hours": "h",
        "unit_minutes": "min",
        "placeholder_select_destination": "Selecione Destino...",
        "placeholder_select_source": "Selecione Origem...",
        
        # Popups de Frequência e Dias
        "title_freq_popup": "Selecionar Frequência / Dias",
        "header_freq_routine": "FREQUÊNCIA DA ROTINA",
        "radio_recurring_days": "Dias Recorrentes",
        "radio_single_date": "Data Única",
        "btn_confirm_freq": "CONFIRMAR FREQUÊNCIA",
        "title_select_days": "Selecionar Dias",
        "header_select_days": "SELECIONE OS DIAS DA SEMANA",
        
        # Popups de Seleção Geral (Origem, Destino, Hora, Minuto)
        "lbl_filter": "Filtrar:",
        "btn_confirm_selection": "CONFIRMAR SELEÇÃO",
        "title_select_destination": "Selecionar Destino",
        "header_select_destination": "SELECIONE O DESTINO",
        "title_select_source": "Selecionar Origem",
        "header_select_source": "SELECIONE A ORIGEM",
        "title_select_hour": "Selecionar Hora",
        "header_select_hour": "SELECIONE A HORA",
        "unit_hours_plural": "Horas",
        "title_select_minute": "Selecionar Minuto",
        "header_select_minute": "SELECIONE O MINUTO",
        "unit_minutes_plural": "Minutos",
        
        # Frequências e Dias
        "freq_everyday": "Todos os Dias",
        "freq_every_day": "Todos os Dias",
        "freq_once": "Apenas Uma Vez",
        "day_monday": "Segunda-feira",
        "day_tuesday": "Terça-feira",
        "day_wednesday": "Quarta-feira",
        "day_thursday": "Quinta-feira",
        "day_friday": "Sexta-feira",
        "day_saturday": "Sábado",
        "day_sunday": "Domingo",

        # Mapeamento Numérico dos Dias (Index 0-6)
        "day_0": "Segunda-feira",
        "day_1": "Terça-feira",
        "day_2": "Quarta-feira",
        "day_3": "Quinta-feira",
        "day_4": "Sexta-feira",
        "day_5": "Sábado",
        "day_6": "Domingo",
        
        # Siglas dos Dias (Exibição Curta)
        "day_mon_short": "seg",
        "day_tue_short": "ter",
        "day_wed_short": "qua",
        "day_thu_short": "qui",
        "day_fri_short": "sex",
        "day_sat_short": "sab",
        "day_sun_short": "dom",
        
        # Tabela e Status
        "btn_add_schedule": "ADICIONAR AGENDAMENTO",
        "btn_save_changes": "SALVAR ALTERAÇÕES",
        "btn_cancel_edit": "CANCELAR EDIÇÃO",
        "col_id": "#",
        "col_destination": "Destino (Saída Matriz)",
        "col_source": "Origem (Entrada Matriz)",
        "col_frequency": "Frequência / Data",
        "col_time": "Horário",
        "col_status": "Status",
        "status_waiting_time": "AGUARDANDO HORÁRIO",
        "status_executed": "EXECUTADO",
        "status_disabled": "DESATIVADO",
        "btn_remove_selected": "REMOVER SELECIONADO",
        "btn_edit_selected": "EDITAR SELECIONADO",
        "btn_run_now": "EXECUTAR SELECIONADO AGORA",
        "footer_engineering_team": "Desenvolvido por Gabriel Menge",
        
        # Aba Real-Time Monitoring
        "rt_panel_title": "PAINEL DE MONITORAÇÃO DE ROTINAS DA MATRIZ",
        "rt_destination_prefix": "DESTINO",
        "rt_status_waiting": "AGUARDANDO",
        "rt_status_executed": "EXECUTADO",
        "rt_no_schedules_msg": "Nenhum destino possui rotinas agendadas no momento.",

        # Aba Configurações (Settings)
        "settings_net_config_title": "Configuração de Rede (Matriz AJA KUMO)",
        "settings_ip_label": "Endereço IP da Matriz:",
        "settings_btn_save_ip": "SALVAR IP",
        "settings_ip_in_use": "IP Atual em Uso:",
        "settings_inputs_title": "Gerenciamento de Entradas (Origens)",
        "settings_inputs_list": "Lista de Origens (1 a 64):",
        "settings_outputs_title": "Gerenciamento de Saídas (Destinos)",
        "settings_outputs_list": "Lista de Destinos (1 a 64):",
        "settings_filter_placeholder": "Filtrar:",
        "settings_btn_edit_label": "Editar Rótulo",
        "settings_language_label": "Idioma do Sistema / Language:",
        
        # Chaves de Edição de Rótulos
        "lbl_list_64_pattern": "Lista (Portas 01 a 64):",
        "btn_edit_label": "Editar Rótulo",
        "title_edit_label": "Editar Nome do Rótulo",
        "lbl_new_label_name": "Novo Nome para o Rótulo:",
        "msg_label_updated_title": "Sucesso",
        "msg_label_updated_text": "Rótulo atualizado com sucesso!",
    },
    "en_US": {
        # Matrix IP Selection
        "lbl_source_single": "Source",
        "lbl_destination_single": "Destination",
        "title_edit_selected": "EDIT SELECTED - {type} [{num:02d}]",
        "msg_select_item_edit_type": "Please select a schedule from the list to edit.",
        "ip_title": "AjaSchedule - IP Configuration",
        "ip_instruction": "Enter the Matrix server IP address:",
        "btn_save_continue": "Save & Continue",
        "ip_warning_empty": "IP address cannot be empty!",
        "warning_title": "Warning",

        # IP Validation & Change
        "msg_invalid_ip_title": "Invalid IP",
        "msg_invalid_ip_text": "The entered IP address is invalid. Please check and try again.",
        "msg_ip_updated_success": "Matrix IP address updated successfully!",
        "msg_success_title": "Success",
        "lbl_current_ip": "Current IP:",
        "log_ip_changed": "Matrix IP changed to {new}",

        # Factory Default Labels (Inputs / Outputs)
        "default_input_label": "Source {num}",
        "default_output_label": "Destination {num}",

        # System Logs & Connection
        "log_initialized": "System initialized.",
        "log_conn_failed": "Failed to connect to Matrix at IP {ip}.",
        "log_init_app": "System initialized and ready.",
        "log_init_testing_conn": "Testing connection with Matrix at IP {ip}...",
        "log_init_conn_success": "Successfully connected to Matrix ({ip}).",
        "log_init_conn_status": "Matrix response ({ip}): HTTP Status {status}.",
        "log_init_conn_timeout": "Connection timed out at IP {ip}.",
        "log_init_conn_failed": "Network error connecting to Matrix at IP {ip}.",
        "log_save_agendamentos_failed": "Failed to save schedules.",
        "log_status_check_failed": "Failed to query status for Destination [{dest}].",
        "log_conn_unreachable": "Matrix at IP {ip} is unreachable on the network.",
        "log_time_at": "at",

        # Schedule Actions Logs
        "err_http_switch": "HTTP Error {code} switching Destination [{dest:02d}].",
        "err_connection_switch": "Switch failed: Matrix at IP {ip} unreachable.",
        "log_routine_updated": "Routine updated: Destination [{dest_new}] <- Source [{src_new}] {time_at} {time_new}",
        "log_routine_added": "Routine created: Destination [{dest}] <- Source [{src}] {time_at} {time}",
        "log_routine_deleted": "Routine removed: Destination [{dest}]",
        "log_routine_removed": "Routine removed: Destination [{dest}] <- Source [{src}]",
        "log_single_event_removed": "Event removed: Destination [{dest}] <- Source [{src}]",
        "log_routine_executed": "Switch executed successfully: Destination [{dest}] <- Source [{src}]",

        # General UI & Alerts
        "lbl_event_date": "Event Date (YYYY-MM-DD):",
        "msg_select_item_title": "Warning",
        "msg_select_item_edit": "Please select a schedule from the list to edit.",
        "msg_select_item_delete": "Please select a schedule from the list to delete.",
        "msg_select_item_run": "Please select a schedule from the list to run.",
        "msg_confirm_delete_title": "Confirm Deletion",
        "msg_confirm_delete_text": "Are you sure you want to delete the selected schedule?",
        "app_title": "KUMO 64x64 Scheduler",
        "btn_cancel": "CANCEL",
        "btn_confirm": "CONFIRM",
        "btn_save": "SAVE",
        
        # Tabs
        "tab_schedule": "Schedule Switches",
        "tab_monitor": "Real-Time Monitoring",
        "tab_logs": "System Logs",
        "tab_config": "Settings",
        
        # Schedule Form
        "frame_new_schedule": "NEW ROUTINE SCHEDULE",
        "lbl_destination": "Destination:",
        "lbl_source": "Source:",
        "lbl_frequency": "Frequency:",
        "lbl_time": "Time:",
        "btn_now": "NOW",
        "btn_add_schedule_action": "+ SCHEDULE",
        "unit_hours": "h",
        "unit_minutes": "min",
        "placeholder_select_destination": "Select Destination...",
        "placeholder_select_source": "Select Source...",
        
        # Frequency Popups & Days
        "title_freq_popup": "Select Frequency / Days",
        "header_freq_routine": "ROUTINE FREQUENCY",
        "radio_recurring_days": "Recurring Days",
        "radio_single_date": "Single Date",
        "btn_confirm_freq": "CONFIRM FREQUENCY",
        "title_select_days": "Select Days",
        "header_select_days": "SELECT DAYS OF THE WEEK",
        
        # General Selection Popups (Source, Destination, Hour, Minute)
        "lbl_filter": "Filter:",
        "btn_confirm_selection": "CONFIRM SELECTION",
        "title_select_destination": "Select Destination",
        "header_select_destination": "SELECT DESTINATION",
        "title_select_source": "Select Source",
        "header_select_source": "SELECT SOURCE",
        "title_select_hour": "Select Hour",
        "header_select_hour": "SELECT HOUR",
        "unit_hours_plural": "Hours",
        "title_select_minute": "Select Minute",
        "header_select_minute": "SELECT MINUTE",
        "unit_minutes_plural": "Minutes",
        
        # Frequencies and Days
        "freq_everyday": "Every Day",
        "freq_every_day": "Every Day",
        "freq_once": "Once Only",
        "day_monday": "Monday",
        "day_tuesday": "Tuesday",
        "day_wednesday": "Wednesday",
        "day_thursday": "Thursday",
        "day_friday": "Friday",
        "day_saturday": "Saturday",
        "day_sunday": "Sunday",

        # Numerical Days Mapping (Index 0-6)
        "day_0": "Monday",
        "day_1": "Tuesday",
        "day_2": "Wednesday",
        "day_3": "Thursday",
        "day_4": "Friday",
        "day_5": "Saturday",
        "day_6": "Sunday",
        
        # Day Short Codes (Card Display)
        "day_mon_short": "Mon",
        "day_tue_short": "Tue",
        "day_wed_short": "Wed",
        "day_thu_short": "Thu",
        "day_fri_short": "Fri",
        "day_sat_short": "Sat",
        "day_sun_short": "Sun",
        
        # Table and Status
        "btn_add_schedule": "ADD SCHEDULE",
        "btn_save_changes": "SAVE CHANGES",
        "btn_cancel_edit": "CANCEL EDIT",
        "col_id": "#",
        "col_destination": "Destination (Matrix Output)",
        "col_source": "Source (Matrix Input)",
        "col_frequency": "Frequency / Date",
        "col_time": "Time",
        "col_status": "Status",
        "status_waiting_time": "WAITING FOR TIME",
        "status_executed": "EXECUTED",
        "status_disabled": "DISABLED",
        "btn_remove_selected": "REMOVE SELECTED",
        "btn_edit_selected": "EDIT SELECTED",
        "btn_run_now": "RUN SELECTED NOW",
        "footer_engineering_team": "Created by Gabriel Menge",
        
        # Real-Time Monitoring Tab
        "rt_panel_title": "MATRIX ROUTINE MONITORING PANEL",
        "rt_destination_prefix": "DESTINATION",
        "rt_status_waiting": "WAITING",
        "rt_status_executed": "EXECUTED",
        "rt_no_schedules_msg": "No destinations have scheduled routines at the moment.",

        # Settings Tab
        "settings_net_config_title": "Network Configuration (AJA KUMO Router)",
        "settings_ip_label": "Router IP Address:",
        "settings_btn_save_ip": "SAVE IP",
        "settings_ip_in_use": "Current IP in Use:",
        "settings_inputs_title": "Input Management (Sources)",
        "settings_inputs_list": "Sources List (1 to 64):",
        "settings_outputs_title": "Output Management (Destinations)",
        "settings_outputs_list": "Destinations List (1 to 64):",
        "settings_filter_placeholder": "Filter:",
        "settings_btn_edit_label": "Edit Label",
        "settings_language_label": "System Language / Idioma:",
        
        # Labels Editing
        "lbl_list_64_pattern": "List (Ports 01 to 64):",
        "btn_edit_label": "Edit Label",
        "title_edit_label": "Edit Label Name",
        "lbl_new_label_name": "New Name for Label:",
        "msg_label_updated_title": "Success",
        "msg_label_updated_text": "Label updated successfully!",
    },
    "es_ES": {
        # Selección de IP de Matriz
        "lbl_source_single": "Origen",
        "lbl_destination_single": "Destino",
        "title_edit_selected": "EDITAR SELECCIÓN - {type} [{num:02d}]",
        "msg_select_item_edit_type": "Por favor, seleccione una programación de la lista para editar.",
        "ip_title": "AjaSchedule - Configuración de IP",
        "ip_instruction": "Ingrese la IP del servidor de Matriz:",
        "btn_save_continue": "Guardar y Continuar",
        "ip_warning_empty": "¡La dirección IP no puede estar vacía!",
        "warning_title": "Aviso",

        # Validación y Cambio de IP
        "msg_invalid_ip_title": "IP Inválida",
        "msg_invalid_ip_text": "La dirección IP ingresada no es válida. Por favor, verifique e intente nuevamente.",
        "msg_ip_updated_success": "¡Dirección IP de la Matriz actualizada con éxito!",
        "msg_success_title": "Éxito",
        "lbl_current_ip": "IP Actual:",
        "log_ip_changed": "IP de la Matriz cambiada a {new}",

        # Etiquetas Por Defecto de Fábrica (Entradas / Salidas)
        "default_input_label": "Origen {num}",
        "default_output_label": "Destino {num}",

        # Logs del Sistema y Conexión
        "log_initialized": "Sistema inicializado.",
        "log_conn_failed": "Error al conectar con la Matriz en la IP {ip}.",
        "log_init_app": "Sistema inicializado y listo.",
        "log_init_testing_conn": "Probando conexión con la Matriz en la IP {ip}...",
        "log_init_conn_success": "Conectado con éxito a la Matriz ({ip}).",
        "log_init_conn_status": "Respuesta de la Matriz ({ip}): Estado HTTP {status}.",
        "log_init_conn_timeout": "Tiempo de espera agotado en la IP {ip}.",
        "log_init_conn_failed": "Error de red al conectar a la Matriz en la IP {ip}.",
        "log_save_agendamentos_failed": "Error al guardar programaciones.",
        "log_status_check_failed": "Error al consultar el estado del Destino [{dest}].",
        "log_conn_unreachable": "Matriz en la IP {ip} no está accesible en la red.",
        "log_time_at": "a las",

        # Logs de Acciones
        "err_http_switch": "Error HTTP {code} al conmutar Destino [{dest:02d}].",
        "err_connection_switch": "Fallo al conmutar: Matriz en la IP {ip} inaccesible.",
        "log_routine_updated": "Rutina actualizada: Destino [{dest_new}] <- Origen [{src_new}] {time_at} {time_new}",
        "log_routine_added": "Rutina creada: Destino [{dest}] <- Origen [{src}] {time_at} {time}",
        "log_routine_deleted": "Rutina eliminada: Destino [{dest}]",
        "log_routine_removed": "Rutina eliminada: Destino [{dest}] <- Origen [{src}]",
        "log_single_event_removed": "Evento eliminado: Destino [{dest}] <- Origen [{src}]",
        "log_routine_executed": "Conmutación ejecutada con éxito: Destino [{dest}] <- Origen [{src}]",

        # Interfaz General
        "lbl_event_date": "Fecha del Evento (AAAA-MM-DD):",
        "msg_select_item_title": "Atención",
        "msg_select_item_edit": "Por favor, seleccione una programación de la lista para editar.",
        "msg_select_item_delete": "Por favor, seleccione una programación de la lista para eliminar.",
        "msg_select_item_run": "Por favor, seleccione una programación de la lista para ejecutar.",
        "msg_confirm_delete_title": "Confirmar Eliminación",
        "msg_confirm_delete_text": "¿Está seguro de que desea eliminar la programación seleccionada?",
        "app_title": "Programador KUMO 64x64",
        "btn_cancel": "CANCELAR",
        "btn_confirm": "CONFIRMAR",
        "btn_save": "GUARDAR",
        
        # Pestañas
        "tab_schedule": "Programar Conmutaciones",
        "tab_monitor": "Monitoreo en Tiempo Real",
        "tab_logs": "Logs del Sistema",
        "tab_config": "Configuración",
        
        # Formulario
        "frame_new_schedule": "NUEVA PROGRAMACIÓN DE RUTINA",
        "lbl_destination": "Destino:",
        "lbl_source": "Origen:",
        "lbl_frequency": "Frecuencia:",
        "lbl_time": "Hora:",
        "btn_now": "AHORA",
        "btn_add_schedule_action": "+ PROGRAMAR",
        "unit_hours": "h",
        "unit_minutes": "min",
        "placeholder_select_destination": "Seleccione Destino...",
        "placeholder_select_source": "Seleccione Origen...",
        
        # Popups
        "title_freq_popup": "Seleccionar Frecuencia / Días",
        "header_freq_routine": "FRECUENCIA DE LA RUTINA",
        "radio_recurring_days": "Días Recurrentes",
        "radio_single_date": "Fecha Única",
        "btn_confirm_freq": "CONFIRMAR FRECUENCIA",
        "title_select_days": "Seleccionar Días",
        "header_select_days": "SELECCIONE LOS DÍAS DE LA SEMANA",
        "lbl_filter": "Filtrar:",
        "btn_confirm_selection": "CONFIRMAR SELECCIÓN",
        "title_select_destination": "Seleccionar Destino",
        "header_select_destination": "SELECCIONE EL DESTINO",
        "title_select_source": "Seleccionar Origem",
        "header_select_source": "SELECCIONE EL ORIGEN",
        "title_select_hour": "Seleccionar Hora",
        "header_select_hour": "SELECCIONE LA HORA",
        "unit_hours_plural": "Horas",
        "title_select_minute": "Seleccionar Minuto",
        "header_select_minute": "SELECCIONE EL MINUTO",
        "unit_minutes_plural": "Minutos",
        
        # Días y Frecuencias
        "freq_everyday": "Todos los Días",
        "freq_every_day": "Todos los Días",
        "freq_once": "Una Sola Vez",
        "day_monday": "Lunes",
        "day_tuesday": "Martes",
        "day_wednesday": "Miércoles",
        "day_thursday": "Jueves",
        "day_friday": "Viernes",
        "day_saturday": "Sábado",
        "day_sunday": "Domingo",

        # Mapeo Numérico de Días (Index 0-6)
        "day_0": "Lunes",
        "day_1": "Martes",
        "day_2": "Miércoles",
        "day_3": "Jueves",
        "day_4": "Viernes",
        "day_5": "Sábado",
        "day_6": "Domingo",
        
        "day_mon_short": "lun",
        "day_tue_short": "mar",
        "day_wed_short": "mié",
        "day_thu_short": "jue",
        "day_fri_short": "vie",
        "day_sat_short": "sáb",
        "day_sun_short": "dom",
        
        # Tabla y Botones
        "btn_add_schedule": "AGREGAR PROGRAMACIÓN",
        "btn_save_changes": "GUARDAR CAMBIOS",
        "btn_cancel_edit": "CANCELAR EDICIÓN",
        "col_id": "#",
        "col_destination": "Destino (Salida Matriz)",
        "col_source": "Origen (Entrada Matriz)",
        "col_frequency": "Frecuencia / Fecha",
        "col_time": "Hora",
        "col_status": "Estado",
        "status_waiting_time": "ESPERANDO HORA",
        "status_executed": "EJECUTADO",
        "status_disabled": "DESACTIVADO",
        "btn_remove_selected": "ELIMINAR SELECCIONADO",
        "btn_edit_selected": "EDITAR SELECCIONADO",
        "btn_run_now": "EJECUTAR AHORA",
        "footer_engineering_team": "Desarrollado por Gabriel Menge",
        
        # Monitoreo
        "rt_panel_title": "PANEL DE MONITOREO DE RUTINAS DE LA MATRIZ",
        "rt_destination_prefix": "DESTINO",
        "rt_status_waiting": "ESPERANDO",
        "rt_status_executed": "EJECUTADO",
        "rt_no_schedules_msg": "Ningún destino tiene rutinas programadas en este momento.",

        # Pestaña Configuración
        "settings_net_config_title": "Configuración de Red (Matriz AJA KUMO)",
        "settings_ip_label": "Dirección IP de la Matriz:",
        "settings_btn_save_ip": "GUARDAR IP",
        "settings_ip_in_use": "IP Actual en Uso:",
        "settings_inputs_title": "Gestión de Entradas (Orígenes)",
        "settings_inputs_list": "Lista de Orígenes (1 a 64):",
        "settings_outputs_title": "Gestión de Salidas (Destinos)",
        "settings_outputs_list": "Lista de Destinos (1 a 64):",
        "settings_filter_placeholder": "Filtrar:",
        "settings_btn_edit_label": "Editar Etiqueta",
        "settings_language_label": "Idioma del Sistema / Language:",
        
        # Edición de Etiquetas
        "lbl_list_64_pattern": "Lista (Puertos 01 a 64):",
        "btn_edit_label": "Editar Etiqueta",
        "title_edit_label": "Editar Nombre de la Etiqueta",
        "lbl_new_label_name": "Nuevo Nombre para la Etiqueta:",
        "msg_label_updated_title": "Éxito",
        "msg_label_updated_text": "¡Etiqueta actualizada con éxito!",
    }
}


class I18n:
    """Gerenciador central de i18n para suporte a dicionários dinâmicos."""
    _lang = "pt_BR"

    @classmethod
    def set_language(cls, lang_code: str):
        if lang_code in LOCALES:
            cls._lang = lang_code

    @classmethod
    def get_language(cls) -> str:
        return cls._lang

    @classmethod
    def t(cls, key: str, **kwargs) -> str:
        dict_lang = LOCALES.get(cls._lang, LOCALES["pt_BR"])
        text = dict_lang.get(key, LOCALES["pt_BR"].get(key, key))
        if kwargs:
            try:
                return text.format(**kwargs)
            except (KeyError, ValueError):
                return text
        return text


# Alias global para facilidade de chamada nos scripts: _("btn_confirm")
_ = I18n.t


def obter_nome_porta(valor_config: str) -> str:
    """
    Recebe a string salva no config.json (ex: 'default_input_label:1' ou 'Câmera Estúdio 1')
    e devolve a tradução adequada ou o texto personalizado.
    """
    if valor_config and ":" in valor_config:
        chave, num = valor_config.split(":", 1)
        return _(chave, num=num)
    
    return valor_config
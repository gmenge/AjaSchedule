import json
import os

LOCALES = {
    "pt_BR": {
        # Rótulos Padrão de Fábrica (Entradas / Saídas)
        "default_input_label": "Origem {num}",
        "default_output_label": "Destino {num}",

        # Logs do Sistema e Conexão
        "log_initialized": "AjaSchedule inicializado e operacional.",
        "log_conn_failed": "[INICIALIZAÇÃO] FALHA DE CONEXÃO: Tempo limite esgotado (Timeout de 3s). Matriz KUMO no IP {ip} não respondeu.",
        "log_init_app": "AjaSchedule inicializado e operacional.",
        "log_init_testing_conn": "[INICIALIZAÇÃO] Testando conexão com a Matriz KUMO ({ip})...",
        "log_init_conn_success": "[INICIALIZAÇÃO] CONEXÃO BEM-SUCEDIDA com a Matriz KUMO ({ip}) - Equipamento Online e Operacional.",
        "log_init_conn_status": "[INICIALIZAÇÃO] Matriz KUMO ({ip}) respondeu com Status HTTP {status}.",
        "log_init_conn_timeout": "[INICIALIZAÇÃO] FALHA DE CONEXÃO: Tempo limite esgotado (Timeout de 3s). Matriz KUMO no IP {ip} não respondeu.",
        "log_init_conn_failed": "[INICIALIZAÇÃO] FALHA DE CONEXÃO: Matriz KUMO ({ip}) inacessível. Erro: {err}",
        "log_save_agendamentos_failed": "Falha ao salvar agendamentos no disco: {err}",
        "log_status_check_failed": "Não foi possível consultar estado prévio do Destino [{dest}]: {err}",
        "log_conn_unreachable": "FALHA DE CONEXÃO: Matriz KUMO [{ip}] inacessível na rede! Erro: {err}",
        "log_time_at": "às",
        
        # Logs de Ações de Agendamento
        "log_routine_updated": "ROTINA ATUALIZADA (ID #{id} | UUID: {uuid}): [DE] Destino [{dest_old}] <- Origem [{src_old}] {time_at} {time_old} | [PARA] Destino [{dest_new}] <- Origem [{src_new}] {time_at} {time_new}",
        "log_routine_added": "ROTINA ADICIONADA (ID #{id} | UUID: {uuid}): Destino [{dest}] <- Origem [{src}] {time_at} {time} | Frequência: {freq}",
        "log_routine_deleted": "ROTINA REMOVIDA (ID #{id} | UUID: {uuid}): Destino [{dest}]",
        "log_routine_removed": "ROTINA REMOVIDA (ID #{id} | UUID: {uuid}): Destino [{dest}] <- Origem [{src}] {time_at} {time} | Frequência: {freq}",
        "log_single_event_removed": "EVENTO ÚNICO REMOVIDO (ID #{id} | UUID: {uuid}): Destino [{dest}] <- Origem [{src}] {time_at} {time} | Frequência: {freq}",
        "log_routine_executed": "ROTINA EXECUTADA COM SUCESSO: Destino [{dest}] <- Origem [{src}]",
        
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
        
        # Chaves Adicionadas / Corrigidas das Revisões
        "lbl_list_64_pattern": "Lista (Portas 01 a 64):",
        "btn_edit_label": "Editar Rótulo",
        "title_edit_label": "Editar Nome do Rótulo",
        "lbl_new_label_name": "Novo Nome para o Rótulo:",
        "msg_label_updated_title": "Sucesso",
        "msg_label_updated_text": "Rótulo atualizado com sucesso!",
    },
    "en_US": {
        # Factory Default Labels (Inputs / Outputs)
        "default_input_label": "Source {num}",
        "default_output_label": "Destination {num}",

        # System Logs & Connection
        "log_initialized": "AjaSchedule initialized and operational.",
        "log_conn_failed": "[INITIALIZATION] CONNECTION FAILED: Timeout reached (3s Timeout). KUMO Matrix at IP {ip} did not respond.",
        "log_init_app": "AjaSchedule initialized and operational.",
        "log_init_testing_conn": "[INITIALIZATION] Testing connection with KUMO Matrix ({ip})...",
        "log_init_conn_success": "[INITIALIZATION] CONNECTION SUCCESSFUL with KUMO Matrix ({ip}) - Device Online and Operational.",
        "log_init_conn_status": "[INITIALIZATION] KUMO Matrix ({ip}) responded with HTTP Status {status}.",
        "log_init_conn_timeout": "[INITIALIZATION] CONNECTION FAILED: Timeout (3s limit). KUMO Matrix at IP {ip} did not respond.",
        "log_init_conn_failed": "[INITIALIZATION] CONNECTION FAILED: KUMO Matrix ({ip}) unreachable. Error: {err}",
        "log_save_agendamentos_failed": "Failed to save schedules to disk: {err}",
        "log_status_check_failed": "Could not query previous status for Destination [{dest}]: {err}",
        "log_conn_unreachable": "CONNECTION FAILED: KUMO Matrix [{ip}] unreachable on network! Error: {err}",
        "log_time_at": "at",

        # Schedule Actions Logs
        "log_routine_updated": "ROUTINE UPDATED (ID #{id} | UUID: {uuid}): [FROM] Destination [{dest_old}] <- Source [{src_old}] {time_at} {time_old} | [TO] Destination [{dest_new}] <- Source [{src_new}] {time_at} {time_new}",
        "log_routine_added": "ROUTINE ADDED (ID #{id} | UUID: {uuid}): Destination [{dest}] <- Source [{src}] {time_at} {time} | Frequency: {freq}",
        "log_routine_deleted": "ROUTINE REMOVED (ID #{id} | UUID: {uuid}): Destination [{dest}]",
        "log_routine_removed": "ROUTINE REMOVED (ID #{id} | UUID: {uuid}): Destination [{dest}] <- Source [{src}] {time_at} {time} | Frequency: {freq}",
        "log_single_event_removed": "SINGLE EVENT REMOVED (ID #{id} | UUID: {uuid}): Destination [{dest}] <- Source [{src}] {time_at} {time} | Frequency: {freq}",
        "log_routine_executed": "ROUTINE EXECUTED SUCCESSFULLY: Destination [{dest}] <- Source [{src}]",

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
        
        # Added / Fixed Keys from Reviews
        "lbl_list_64_pattern": "List (Ports 01 to 64):",
        "btn_edit_label": "Edit Label",
        "title_edit_label": "Edit Label Name",
        "lbl_new_label_name": "New Name for Label:",
        "msg_label_updated_title": "Success",
        "msg_label_updated_text": "Label updated successfully!",
    },
    "es_ES": {
        # Etiquetas Por Defecto de Fábrica (Entradas / Salidas)
        "default_input_label": "Origen {num}",
        "default_output_label": "Destino {num}",

        # Logs del Sistema y Conexión
        "log_initialized": "AjaSchedule inicializado y operativo.",
        "log_conn_failed": "[INICIALIZACIÓN] ERROR DE CONEXIÓN: Tiempo de espera agotado (Timeout 3s). Matriz KUMO en la IP {ip} no respondió.",
        "log_init_app": "AjaSchedule inicializado y operativo.",
        "log_init_testing_conn": "[INICIALIZACIÓN] Probando conexión con la Matriz KUMO ({ip})...",
        "log_init_conn_success": "[INICIALIZACIÓN] CONEXIÓN EXITOSA con la Matriz KUMO ({ip}) - Equipo Online y Operativo.",
        "log_init_conn_status": "[INICIALIZACIÓN] Matriz KUMO ({ip}) respondió con Estado HTTP {status}.",
        "log_init_conn_timeout": "[INICIALIZACIÓN] ERROR DE CONEXIÓN: Tiempo agotado (3s). Matriz KUMO en la IP {ip} no respondió.",
        "log_init_conn_failed": "[INICIALIZACIÓN] ERROR DE CONEXIÓN: Matriz KUMO ({ip}) inaccesible. Error: {err}",
        "log_save_agendamentos_failed": "Error al guardar programaciones en disco: {err}",
        "log_status_check_failed": "No se pudo consultar el estado previo del Destino [{dest}]: {err}",
        "log_conn_unreachable": "ERROR DE CONEXIÓN: ¡Matriz KUMO [{ip}] inaccesible en la red! Error: {err}",
        "log_time_at": "a las",

        # Logs de Acciones
        "log_routine_updated": "RUTINA ACTUALIZADA (ID #{id} | UUID: {uuid}): [DE] Destino [{dest_old}] <- Origen [{src_old}] {time_at} {time_old} | [PARA] Destino [{dest_new}] <- Origen [{src_new}] {time_at} {time_new}",
        "log_routine_added": "RUTINA AGREGADA (ID #{id} | UUID: {uuid}): Destino [{dest}] <- Origen [{src}] {time_at} {time} | Frecuencia: {freq}",
        "log_routine_deleted": "RUTINA ELIMINADA (ID #{id} | UUID: {uuid}): Destino [{dest}]",
        "log_routine_removed": "RUTINA ELIMINADA (ID #{id} | UUID: {uuid}): Destino [{dest}] <- Origen [{src}] {time_at} {time} | Frecuencia: {freq}",
        "log_single_event_removed": "EVENTO ÚNICO ELIMINADO (ID #{id} | UUID: {uuid}): Destino [{dest}] <- Origen [{src}] {time_at} {time} | Frecuencia: {freq}",
        "log_routine_executed": "RUTINA EJECUTADA CON ÉXITO: Destino [{dest}] <- Origen [{src}]",

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
        "title_select_source": "Seleccionar Origen",
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
        "footer_engineering_team": "Desenvolvido por Gabriel Menge",
        
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
        
        # Claves agregadas / corregidas de las revisiones
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
            except KeyError:
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


def obter_ou_perguntar_idioma(app_instance=None, config_file="config.json") -> str:
    """
    Recupera o idioma salvo no arquivo JSON.
    Se não existir (1ª execução), exibe um popup Tkinter para escolha.
    """
    if os.path.exists(config_file):
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                lang = data.get("idioma")
                if lang in LOCALES:
                    I18n.set_language(lang)
                    return lang
        except Exception:
            pass

    # --- PRIMEIRA EXECUÇÃO: Pergunta via Janela GUI ---
    import tkinter as tk
    from tkinter import ttk

    escolha = {"lang": "pt_BR"}  # Idioma padrão caso feche no 'X'

    dialog = tk.Tk()
    dialog.title("AjaSchedule - Select Language / Selecionar Idioma")
    dialog.geometry("360x180")
    dialog.resizable(False, False)
    
    # Força a janela a ficar visível e na frente de tudo
    dialog.attributes("-topmost", True)
    dialog.eval('tk::PlaceWindow . center')

    tk.Label(
        dialog, 
        text="Selecione o Idioma / Select Language:", 
        font=("Segoe UI", 10, "bold"),
        pady=10
    ).pack()

    combo = ttk.Combobox(
        dialog, 
        values=["Português (pt_BR)", "English (en_US)", "Español (es_ES)"], 
        state="readonly",
        width=25
    )
    combo.current(0)
    combo.pack(pady=5)

    def confirmar():
        sel = combo.get()
        if "en_US" in sel:
            escolha["lang"] = "en_US"
        elif "es_ES" in sel:
            escolha["lang"] = "es_ES"
        else:
            escolha["lang"] = "pt_BR"
            
        # Salva a escolha no config.json
        try:
            cfg = {}
            if os.path.exists(config_file):
                with open(config_file, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
            cfg["idioma"] = escolha["lang"]
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=4)
        except Exception as e:
            print(f"Erro ao salvar config: {e}")

        dialog.destroy()

    btn = tk.Button(dialog, text="OK / Confirmar", command=confirmar, width=15)
    btn.pack(pady=15)

    dialog.mainloop()

    I18n.set_language(escolha["lang"])
    return escolha["lang"]

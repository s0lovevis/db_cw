import datetime
import streamlit as st
import pandas as pd
from connect import get_connection


def render_transaction_report():
    st.title("📊 Отчёт по транзакциям")
    st.markdown("Выберите период для отчёта по успешным транзакциям:")

    # Выбор периода
    start_date = st.date_input("Дата начала периода")
    end_date = st.date_input("Дата окончания периода", value=start_date)

    if st.button("Сформировать отчёт"):
        # Границы периода
        start_dt = datetime.datetime.combine(start_date, datetime.time.min)
        end_dt   = datetime.datetime.combine(end_date, datetime.time.max)

        # Запрос транзакций
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    '''
                    SELECT
                        t.transaction_id,
                        t.transaction_time,
                        c.name           AS товар,
                        s.company_name   AS поставщик,
                        case when t.operation = 'Добавить' then 'Покупка у поставщика' else 'Продажа' end AS операция,
                        t.quantity       AS количество,
                        t.monetary_volume AS объём
                    FROM transactions t
                    JOIN catalog c   ON t.item_id = c.item_id
                    JOIN suppliers s ON c.supplier_id = s.supplier_id
                    WHERE t.success = TRUE
                      AND t.transaction_time BETWEEN %s AND %s
                    ORDER BY t.transaction_time
                    ''',
                    (start_dt, end_dt)
                )
                rows = cur.fetchall()

        if not rows:
            st.info("За выбранный период нет успешных транзакций.")
            return

        # Формируем DataFrame
        df = pd.DataFrame(rows, columns=[
            "ID транзакции", "Время", "Товар", "Поставщик",
            "Операция", "Количество", "Объём"
        ])

        # Считаем суммы: 'Добавить' = трата (отрицательно), 'Удалить' = доход (положительно)
        df["Сумма (₽)"] = df.apply(
            lambda r: -r["Объём"] if r["Операция"].lower() == "покупка у поставщика"
                      else r["Объём"],
            axis=1
        )

        # Вывод таблицы
        st.dataframe(df.drop(columns=["Объём"]), use_container_width=True)

        # Итоговая сумма
        total = df["Сумма (₽)"].sum()
        st.markdown(f"**Итого за период:** {total:,.2f} ₽")

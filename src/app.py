from consts import GlobalState
from utils import format_df, format_cdf, container, apply_filters, ALL_KEYWORD
import traceback
import io
import pandas as pd
import streamlit as st
from models.DfInfo import DfInfo
from scraper.main import retrieve_data
import math


class App:
    def __init__(self):
        st.set_page_config(
            page_title="Ferramenta de Análise de Dados",
            page_icon="📊",
            layout="wide",
        )

        st.title("DM Scraper")

        hide_streamlit_style = """
        <style>
        #MainMenu, .stAppToolbar, footer {visibility: hidden;}
        <style>
        """

        st.markdown(hide_streamlit_style, unsafe_allow_html=True)

        if 'df' not in st.session_state:
            st.session_state.df = pd.DataFrame()

        if 'cdf' not in st.session_state:
            st.session_state.cdf = pd.DataFrame()

        self.include_closed_stores = False

        self.df = st.session_state.df
        self.cdf = st.session_state.cdf
        self.state = GlobalState.FINISHED if self.df.size > 0 else GlobalState.IDLE
        self.df_info = DfInfo(self.df)

    def handle_fetch_data_click(self):
        self.state = GlobalState.FETCHING
        self.render_data_fetch_section()

        try:
            def update_companies(companies):
                self.cdf = pd.concat(
                    [self.cdf, pd.DataFrame(companies)],
                    ignore_index=True,
                )

            def update_products(products):
                self.df_info.df = pd.concat(
                    [self.df_info.df, pd.DataFrame(products)],
                    ignore_index=True,
                )

                self.render_data_preview_section()

            opts = {
                "include_closed_stores": self.include_closed_stores
            }

            retrieve_data(
                cities=st.session_state.cities,
                opts=opts,
                update_product_callback=update_products,
                update_company_callback=update_companies
            )

            self.df = self.df_info.df.copy()
            st.session_state.df = self.df
            st.session_state.cdf = self.cdf
        except Exception as e:
            st.error(f"Erro ao buscar dados: {str(e)}")
            st.error(traceback.format_exc())
        finally:
            self.state = GlobalState.FINISHED
            st.session_state.state = GlobalState.FINISHED

    @container("city_selection")
    def render_city_selection_section(self):
        st.header("🏙️ Seleção de Cidades")

        if 'cities' not in st.session_state:
            st.session_state.cities = []

        c1, c2 = st.columns([0.4, 0.6])

        with c1:
            with st.form("city_form", clear_on_submit=True):
                city_input = st.text_input(
                    "Digite o nome da cidade")
                if st.form_submit_button(label="Adicionar Cidade", use_container_width=True):
                    if city_input:
                        city = city_input.upper()
                        if city in st.session_state.cities:
                            st.toast(
                                f"Cidade '{city_input}' já foi adicionada!")
                        else:
                            st.session_state.cities.append(city_input.upper())
                            st.toast(f"Cidade '{city_input}' adicionada!")
                    else:
                        st.toast("O nome da cidade não pode estar vazio")

        with c2:
            st.subheader("Cidades Selecionadas")
            for city in st.session_state.cities:
                col1, col2 = st.columns([3, 1])
                col1.write(city)
                if col2.button("Remover", key=city):
                    st.session_state.cities.remove(city)
                    st.rerun()

    @container("fetch-options")
    def render_fetch_options_section(self):
        st.header("📁 Dados")

        self.include_closed_stores = st.checkbox(
            "Incluir lojas fechadas")

    @container("fetch")
    def render_data_fetch_section(self):
        button_click = False
        match self.state:
            case GlobalState.IDLE:
                button_click = st.button("Buscar Dados")
            case GlobalState.FETCHING:
                button_click = st.button(
                    "Buscando Dados...",
                    disabled=True
                )
            case GlobalState.FINISHED:
                button_click = st.button("Rebuscar Dados")

        if button_click:
            self.handle_fetch_data_click()

    @container("preview")
    def render_data_preview_section(self):
        if self.state < GlobalState.FETCHING:
            return

        st.header(
            "🔍 Visualização de Dados",
            anchor="data-preview"
        )

        if self.df_info.has_data():
            # Mostrar informações básicas do conjunto de dados
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Informações do Conjunto de Dados")
                st.write(f"Linhas: {self.df_info.rows()}")
                st.write(
                    f"Cidades visitadas: {self.df_info.cities_visited()}")
                st.write(
                    f"Empresas visitadas: {self.df_info.company_visited()}")
                st.write(
                    f"Uso de Memória: {self.df_info.memory_usage()}")

            with col2:
                st.subheader("Pré-visualização dos Dados")

                column_config = {
                    "URL da Empresa": st.column_config.LinkColumn(
                        "URL da Empresa", display_text="Ver Empresa"),
                    "URL da Imagem": st.column_config.ImageColumn("Logo", pinned=True, width=50),
                }

                st.dataframe(
                    format_df(self.df_info.df.head(
                        min(10, self.df_info.df.size))),
                    hide_index=True,
                    use_container_width=True,
                    column_config=column_config
                )

    @container("analysis")
    def render_data_analysis_section(self):
        if self.state < GlobalState.FINISHED:
            return

        st.header("📊 Análise de Dados", anchor="data-analysis")

        original_price_filter_range = (
            float(math.floor(self.df['original_price'].min())),
            float(math.ceil(self.df['original_price'].max()))
        )

        final_price_filter_range = (
            float(math.floor(self.df['final_price'].min())),
            float(math.ceil(self.df['final_price'].max()))
        )

        product_filters = {
            "city": [],
            "category": [],
            "company_name": st.session_state.selected_companies or [],
            "original_price": original_price_filter_range,
            "final_price": final_price_filter_range
        }

        company_filters = {
            "city": [],
            "banners": [],
        }

        product_tab, company_tab = st.tabs(["Produtos", "Empresas"])

        if (self.cdf.size > 0):
            with company_tab:
                c1, c2 = st.columns(2)

                with c1:
                    company_filters['city'] = st.multiselect(
                        "Selecione a cidade",
                        list(self.cdf['city'].unique()),
                        key="company_city_filter"
                    )

                with c2:
                    company_filters['banners'] = st.multiselect(
                        "Selecione os banners", list(filter(bool, self.cdf.explode('banners')['banners'].unique())))

                display_table = apply_filters(self.cdf, company_filters)

                column_config = {
                    "URL da Empresa": st.column_config.LinkColumn(
                        "URL da Empresa", display_text="Ver Empresa"),
                    "Logo": st.column_config.ImageColumn("Logo", pinned=True),
                }

                st.dataframe(
                    format_cdf(display_table),
                    hide_index=True,
                    use_container_width=True,
                    column_config=column_config
                )

                st.session_state.company_filters = company_filters

        if self.df.size > 0:
            with product_tab:
                c1, c2, c3 = st.columns(3)

                with c1:
                    product_filters['city'] = st.multiselect(
                        "Selecione a cidade",
                        list(self.df['city'].unique()),
                        key="product_city_filter"
                    )

                with c2:
                    product_filters["category"] = st.multiselect(
                        "Selecione a categoria",
                        list(self.df['category'].unique())
                    )

                with c3:
                    container = st.empty()
                    container.empty()

                    product_filters["company_name"] = container.multiselect(
                        "Selecione a empresa",
                        list(self.df['company_name'].unique()),
                        product_filters["company_name"]
                    )

                col1, col2 = st.columns(2, gap="large")

                with col1:
                    product_filters['original_price'] = st.slider(
                        "Preço original",
                        min_value=original_price_filter_range[0],
                        max_value=original_price_filter_range[1],
                        value=product_filters['original_price'],
                        step=0.1
                    )

                with col2:
                    product_filters['final_price'] = st.slider(
                        "Preço Final",
                        min_value=final_price_filter_range[0],
                        max_value=final_price_filter_range[1],
                        value=product_filters['final_price'],
                        step=0.1
                    )

                display_table = apply_filters(self.df, product_filters)

                column_config = {
                    "URL da Empresa": st.column_config.LinkColumn(
                        "URL da Empresa", display_text="Ver Empresa"),
                    "URL da Imagem": st.column_config.ImageColumn("Logo", pinned=True),
                }

                st.dataframe(
                    format_df(display_table),
                    hide_index=True,
                    use_container_width=True,
                    column_config=column_config
                )

                st.session_state.product_filters = product_filters

    @container("export")
    def render_data_export_section(self):
        if self.state < GlobalState.FINISHED:
            return

        SHOULD_FORMAT_DF_FILE_FORMATS = ["Excel", "HTML", "Parquet"]

        st.header("💾 Exportação de Dados", anchor="data-export")

        raw_df = None

        if self.df.size > 0:
            selected_df = st.selectbox(
                "Selecione quais dados exportar",
                ["Produtos", "Empresas"],
                index=0
            )

            export_filtered = st.checkbox(
                "Exportar dados filtrados", value=False)

            if selected_df == "Produtos":
                raw_df = self.df.copy()
                raw_filters = st.session_state.product_filters
                def format_fn(df): return format_df(df)
            else:
                raw_df = self.cdf.copy()
                raw_filters = st.session_state.company_filters
                def format_fn(df): return format_cdf(df)

            # Seleção de formato de arquivo
            export_format = st.selectbox(
                "Selecione o formato de exportação",
                ["CSV", "Excel", "JSON", "Parquet", "HTML"]
            )

            # Opções de exportação baseadas no formato
            match export_format:
                case "CSV":
                    col1, col2 = st.columns(2)
                    with col1:
                        delimiter = st.selectbox(
                            "Delimitador", [",", ";", "\t", "|"], index=0)
                    with col2:
                        encoding = st.selectbox(
                            "Codificação", ["utf-8", "latin1", "iso-8859-1", "cp1252"], index=0)
                    include_index = st.checkbox("Incluir índice", value=False)

                case "Excel":
                    sheet_name = st.text_input("Nome da planilha", "Sheet1")
                    include_index = st.checkbox("Incluir índice", value=False)

                case "JSON":
                    orient = st.selectbox("Orientação JSON",
                                          ["records", "columns",
                                           "index", "split", "table"],
                                          index=0)
                    date_format = st.selectbox(
                        "Formato de data", ["epoch", "iso"], index=1)

                case "Parquet":
                    compression = st.selectbox(
                        "Compressão", ["snappy", "gzip", "brotli", "none"], index=0)

            # Botão de exportação
            export_button = st.button("Exportar Dados")

            if export_button:
                if export_filtered:
                    raw_df = apply_filters(raw_df, raw_filters)

                if export_format in SHOULD_FORMAT_DF_FILE_FORMATS:
                    raw_df = format_fn(raw_df)

                try:
                    # Criar buffer em memória para o arquivo
                    buffer = io.BytesIO()

                    if export_format == "CSV":
                        raw_df.to_csv(buffer, sep=delimiter,
                                      index=include_index, encoding=encoding)
                        file_extension = "csv"
                        mime_type = "text/csv"

                    elif export_format == "Excel":
                        raw_df.to_excel(
                            buffer, sheet_name=sheet_name, index=include_index, engine="openpyxl")
                        file_extension = "xlsx"
                        mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

                    elif export_format == "JSON":
                        raw_df.to_json(buffer, orient=orient,
                                       date_format=date_format)
                        file_extension = "json"
                        mime_type = "application/json"

                    elif export_format == "Parquet":
                        compression_arg = None if compression == "none" else compression
                        raw_df.to_parquet(
                            buffer, compression=compression_arg)
                        file_extension = "parquet"
                        mime_type = "application/octet-stream"

                    elif export_format == "HTML":
                        html_content = raw_df.to_html(index=False)
                        buffer.write(html_content.encode())
                        file_extension = "html"
                        mime_type = "text/html"

                    # Preparar botão de download
                    buffer.seek(0)
                    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
                    st.download_button(
                        label=f"Baixar arquivo {export_format}",
                        data=buffer,
                        file_name=f"dados_processados_{timestamp}.{file_extension}",
                        mime=mime_type
                    )

                    st.success(
                        f"Dados prontos para download como {export_format}!")

                except Exception as e:
                    st.error(f"Erro ao exportar dados: {str(e)}")
                    st.error(traceback.format_exc())

    def render(self):
        self.render_city_selection_section()

        # Seção de busca de dados
        self.render_fetch_options_section()
        self.render_data_fetch_section()

        # Se o arquivo for carregado, exibir dados e opções de análise
        # Pré-visualização de dados
        self.render_data_preview_section()

        # Seção de análise de dados
        self.render_data_analysis_section()

        # Seção de exportação de dados
        self.render_data_export_section()


app = App()
app.render()

// Espelha os contratos do backend (snake_case, sem conversão) — [[api/contratos]].

export interface Eixo {
  id: number;
  nome: string;
  cidades: string[];
}

export interface Veiculo {
  nome: string;
  capacidade_peso: number;
  capacidade_volume: number;
  descricao: string;
  selecionavel: boolean;
}

export interface Totais {
  peso_utilizado: number;
  peso_capacidade: number;
  ocupacao_peso: number;
  volume_utilizado: number;
  volume_capacidade: number;
  ocupacao_volume: number;
  valor_total: number;
  quantidade_pedidos: number;
}

export interface ItemPedido {
  codigo: string;
  descricao: string;
  quantidade: number | null;
  unidade_venda: string;
  caixas: number | null;
  peso_total_kg: number | null;
  volume_total_m3: number | null;
  dado_estimado: boolean;
}

export interface PedidoSelecionado {
  ordem: number;
  pedido: string;
  cidade: string;
  valor: number;
  peso_kg: number | null;
  volume_m3: number | null;
  qtd_itens?: number;
  itens?: ItemPedido[];
}

export interface PedidoRejeitado {
  pedido: string;
  cidade: string;
  peso_kg: number | null;
  volume_m3: number | null;
  motivo: string;
}

export interface ParadaDescarga {
  ordem: number;
  cidade: string;
  qtd_pedidos: number;
}

export interface ZonaCarga {
  ordem: number;
  posicao: string;
  cidade: string;
  qtd_pedidos: number;
  peso_kg: number;
  volume_m3: number;
  densidade: number | null;
  pedidos: {
    pedido: string;
    peso_kg: number | null;
    volume_m3: number | null;
    densidade: number | null;
    itens_base: string[];
  }[];
}

export interface OrganizacaoCarga {
  densidade_carga: number | null;
  densidade_veiculo: number | null;
  perfil: string;
  sugestao: string;
  ocupacao_gargalo: number;
  ocupacao_minima: number;
  abaixo_minimo: boolean;
  alerta_minimo: string | null;
  zonas: ZonaCarga[];
}

export interface PlanoDeCarga {
  id: string;
  eixo: Eixo;
  veiculo: Veiculo;
  semana: number | null;
  data_carga: string;
  totais: Totais;
  gargalo: "PESO" | "VOLUME";
  violacoes: number;
  pedidos_selecionados: PedidoSelecionado[];
  pedidos_rejeitados: PedidoRejeitado[];
  sequencia_descarga: ParadaDescarga[];
  orientacao_carregamento: { modo: string; descricao: string };
  organizacao_carga: OrganizacaoCarga;
  gerado_em: string;
}

export interface Pedido {
  pedido: string;
  data: string | null;
  cidade: string;
  eixo_id: number;
  semana: number;
  valor: number | null;
  vendedor: string;
  situacao: string;
  logistica: string;
  peso_kg: number | null;
  volume_m3: number | null;
  qualidade_cubagem: "COMPLETA" | "ESTIMADA" | "AUSENTE";
  elegivel: boolean;
  motivo_exclusao: string | null;
  itens: ItemPedido[];
}

export interface QualidadeResumo {
  registros_processados: number;
  inconsistencias_detectadas: number;
  materiais_ranking: number;
  pedidos_completa: number;
  pedidos_estimada: number;
  pedidos_ausente: number;
  pipeline_stages: { nome: string; registros: number; percentual: number }[];
}

export interface MotivoExclusao {
  codigo: string;
  motivo: string;
  total: number;
  percentual: number;
}

export interface Insight {
  resumo: string;
  modelo: string;
  duracao_ms: number;
}

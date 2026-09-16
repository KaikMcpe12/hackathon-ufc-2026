const nf = (casas: number) =>
  new Intl.NumberFormat("pt-BR", { minimumFractionDigits: casas, maximumFractionDigits: casas });

export const moeda = (v: number | null | undefined) =>
  v == null ? "—" : "R$ " + nf(2).format(v);
export const peso = (v: number | null | undefined) =>
  v == null ? "—" : nf(3).format(v) + " kg";
export const volume = (v: number | null | undefined) =>
  v == null ? "—" : nf(5).format(v) + " m³";
export const pct = (v: number | null | undefined) =>
  v == null ? "—" : nf(1).format(v * 100) + "%";
export const titulo = (s: string) =>
  s.toLowerCase().replace(/(^|\s)\S/g, (c) => c.toUpperCase());

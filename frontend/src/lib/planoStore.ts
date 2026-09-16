import type { PlanoDeCarga } from "../api/types";

const KEY = "nobrelog_plano";

export const savePlano = (p: PlanoDeCarga) => sessionStorage.setItem(KEY, JSON.stringify(p));
export const loadPlano = (): PlanoDeCarga | null => {
  const s = sessionStorage.getItem(KEY);
  return s ? (JSON.parse(s) as PlanoDeCarga) : null;
};

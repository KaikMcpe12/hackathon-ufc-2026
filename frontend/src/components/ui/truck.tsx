// Ilustração de caminhão em CSS (do design de referência).
export function Truck() {
  return (
    <div className="grid h-40 place-items-center" aria-hidden>
      <div className="relative h-[105px] w-[85%]">
        <div className="absolute right-0 top-2 h-[75%] w-[72%] border-2 border-neutral-300 bg-gradient-to-br from-white to-neutral-300">
          <div className="absolute right-[17%] top-[35%] text-2xl font-black tracking-[-3px]">
            N<span className="text-brand">L</span>
          </div>
        </div>
        <div className="absolute bottom-4 left-[2%] h-[58%] w-[30%] rounded-[12px_6px_4px_4px] border-2 border-neutral-400 bg-gradient-to-br from-neutral-100 to-neutral-300" />
        <div className="absolute bottom-0 left-[21%] h-7 w-7 rounded-full border-[7px] border-neutral-700 bg-neutral-900" />
        <div className="absolute bottom-0 right-[10%] h-7 w-7 rounded-full border-[7px] border-neutral-700 bg-neutral-900" />
      </div>
    </div>
  );
}

import { cn } from "cn";
import Image from "next/image";

type Props = { src: string; className?: string; sizes?: string };

export function RemoteImage({ src, className, sizes = "64px" }: Props) {
  return (
    <Image
      src={src}
      alt=""
      fill
      unoptimized
      sizes={sizes}
      className={cn("object-cover", className)}
    />
  );
}

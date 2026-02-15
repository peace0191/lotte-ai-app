import React, { useEffect, useMemo, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import {
    Home,
    Sparkles,
    Bot,
    ClipboardList,
    Video,
    Shield,
    Phone,
    MapPin,
    School,
    Building2,
    Search,
    ArrowRight,
    CheckCircle2,
    CalendarDays,
    MessageSquare,
    Wand2,
    Share2,
    Lock,
} from "lucide-react";

// ------------------------------------------------------------
// ✅ 목적: "대치1동 교육특구" + "AI 저평가매물 자동매칭" + "AI 자동홍보(숏츠)" 를
// 한눈에 보이게 하는 5개 메뉴 데모 (모바일 가독성 최우선)
// ------------------------------------------------------------

// ⚠️ 이미지 경로는 프로젝트의 public/assets 아래에 넣어 주세요.
// 예) public/assets/CEO사진.jpg
const BRAND = {
    officeName: "롯데타워앤강남빌딩부동산중개 (주)",
    ceoName: "이상수",
    phoneMain: "02-578-8285",
    phoneMobile: "010-8985-8945",
    watermark: "롯데타워앤강남빌딩부동산 (주) 02.578.8285",
    assets: {
        ceo: "/assets/CEO사진.jpg",
        businessCard: "/assets/명함.jpg",
        portrait: "/assets/졸업사진.jpg",
    },
};

const MENU = {
    region: { key: "region", label: "지역정보", icon: Home },
    추천매물: { key: "recommend", label: "추천매물", icon: Sparkles },
    ai: { key: "ai", label: "AI 매칭", icon: Bot },
    register: { key: "register", label: "매물등록", icon: ClipboardList },
    shorts: { key: "shorts", label: "숏츠매물", icon: Video },
};

const ADMIN_MENU = [
    { key: "admin_youlab", label: "YOU-LAB", icon: Shield },
    { key: "admin_salespack", label: "영업팩 생성", icon: Shield },
    { key: "admin_system", label: "시스템 설정", icon: Shield },
];

const SCHOOL_ROUTES = [
    {
        id: "route-rapal",
        title: "래미안대치팰리스 / 대치SK뷰",
        line: "대치초 → 대청중 → 숙명여고 → 단대부고",
        tags: ["대장", "학군핵심"],
    },
    {
        id: "route-ipark",
        title: "대치아이파크",
        line: "대도초 → 숙명여중·여고 → 단대부중·부고",
        tags: ["학군", "선호"],
    },
    {
        id: "route-arno",
        title: "삼환아르노보2 (학군 오피스텔)",
        line: "단대부중·부고 / 숙명 / 진선 인근 세컨하우스",
        tags: ["렌트", "세컨"],
    },
];

const SAMPLE_PROPERTIES = [
    {
        id: "p1",
        name: "래미안대치팰리스",
        type: "아파트",
        theme: "학군 대장",
        signal: 92,
        undervalued: true,
        priceNote: "AI 저평가 신호 강함",
        cta: "상담/예약",
    },
    {
        id: "p2",
        name: "대치SK뷰",
        type: "아파트",
        theme: "전입 선호",
        signal: 88,
        undervalued: true,
        priceNote: "전환 가능성 높음",
        cta: "상담/예약",
    },
    {
        id: "p3",
        name: "은마아파트",
        type: "재건축",
        theme: "투자 상징",
        signal: 84,
        undervalued: false,
        priceNote: "재건축 이슈 기반",
        cta: "투자 상담",
    },
    {
        id: "p4",
        name: "시그니엘 레지던스",
        type: "프리미엄",
        theme: "VIP",
        signal: 90,
        undervalued: false,
        priceNote: "VIP 맞춤 전략",
        cta: "VIP 문의",
    },
];

function cn(...xs: Array<string | false | null | undefined>) {
    return xs.filter(Boolean).join(" ");
}

function useAdminGate() {
    const [isAdmin, setIsAdmin] = useState(false);

    useEffect(() => {
        // ✅ 관리자 숨김 규칙: URL에 ?admin=1 이거나, 로컬스토리지 admin=1 일 때만 표시
        const params = new URLSearchParams(window.location.search);
        const q = params.get("admin");
        const ls = window.localStorage.getItem("daechi_admin") || "0";
        if (q === "1" || ls === "1") setIsAdmin(true);
    }, []);

    const toggle = (v: boolean) => {
        setIsAdmin(v);
        window.localStorage.setItem("daechi_admin", v ? "1" : "0");
    };

    return { isAdmin, toggle };
}

function Pillar({
    title,
    desc,
    icon: Icon,
}: {
    title: string;
    desc: string;
    icon: React.ComponentType<any>;
}) {
    return (
        <Card className="rounded-2xl shadow-sm">
            <CardHeader className="pb-2">
                <div className="flex items-center gap-2">
                    <div className="h-9 w-9 rounded-xl border flex items-center justify-center">
                        <Icon className="h-5 w-5" />
                    </div>
                    <CardTitle className="text-base md:text-lg">{title}</CardTitle>
                </div>
            </CardHeader>
            <CardContent className="text-sm text-muted-foreground leading-relaxed">
                {desc}
            </CardContent>
        </Card>
    );
}

function TopBar({
    active,
    setActive,
    isAdmin,
}: {
    active: string;
    setActive: (k: string) => void;
    isAdmin: boolean;
}) {
    const items = Object.values(MENU);
    return (
        <div className="sticky top-0 z-40 backdrop-blur bg-background/75 border-b">
            <div className="mx-auto max-w-6xl px-3 md:px-6 py-2 flex items-center justify-between gap-3">
                <div className="flex items-center gap-2 min-w-0">
                    <div className="h-9 w-9 rounded-xl border flex items-center justify-center shrink-0">
                        <Building2 className="h-5 w-5" />
                    </div>
                    <div className="min-w-0">
                        <div className="text-sm font-semibold truncate">{BRAND.officeName}</div>
                        <div className="text-xs text-muted-foreground truncate">
                            대치1동 교육특구 · AI 저평가매물 · 자동매칭 · 자동홍보
                        </div>
                    </div>
                </div>

                <div className="hidden md:flex items-center gap-2">
                    {items.map((it) => {
                        const Icon = it.icon;
                        const on = active === it.key;
                        return (
                            <Button
                                key={it.key}
                                variant={on ? "default" : "outline"}
                                className="rounded-xl"
                                onClick={() => setActive(it.key)}
                            >
                                <Icon className="h-4 w-4 mr-2" />
                                {it.label}
                            </Button>
                        );
                    })}
                    {isAdmin && (
                        <Badge variant="outline" className="rounded-xl px-3 py-1">
                            <Lock className="h-3.5 w-3.5 mr-1" /> 관리자
                        </Badge>
                    )}
                </div>

                {/* 모바일: 드롭다운 */}
                <div className="md:hidden w-[44%]">
                    <Select value={active} onValueChange={setActive}>
                        <SelectTrigger className="rounded-xl">
                            <SelectValue placeholder="메뉴" />
                        </SelectTrigger>
                        <SelectContent>
                            {items.map((it) => (
                                <SelectItem key={it.key} value={it.key}>
                                    {it.label}
                                </SelectItem>
                            ))}
                            {isAdmin && (
                                <SelectItem value="admin">관리자</SelectItem>
                            )}
                        </SelectContent>
                    </Select>
                </div>
            </div>

            {/* 모바일 하단 빠른탭 */}
            <div className="md:hidden px-3 pb-2">
                <div className="grid grid-cols-5 gap-1">
                    {items.map((it) => {
                        const Icon = it.icon;
                        const on = active === it.key;
                        return (
                            <button
                                key={it.key}
                                onClick={() => setActive(it.key)}
                                className={cn(
                                    "rounded-xl border px-2 py-2 text-[11px] flex flex-col items-center gap-1",
                                    on && "bg-muted"
                                )}
                            >
                                <Icon className="h-4 w-4" />
                                {it.label}
                            </button>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}

function Hero() {
    return (
        <div className="mx-auto max-w-6xl px-3 md:px-6 py-6 md:py-10">
            <div className="grid grid-cols-1 md:grid-cols-12 gap-4 md:gap-6 items-stretch">
                <Card className="rounded-2xl shadow-sm md:col-span-7">
                    <CardHeader>
                        <div className="flex items-start justify-between gap-3">
                            <div className="min-w-0">
                                <div className="text-xs text-muted-foreground">한눈에 이해되는 3가지 핵심</div>
                                <CardTitle className="text-xl md:text-2xl leading-snug">
                                    대치1동 교육특구에 최적화된
                                    <span className="block">AI 저평가매물 추천 · 예약 · 자동계약매칭 · 자동홍보</span>
                                </CardTitle>
                            </div>
                            <Badge className="rounded-xl" variant="secondary">
                                Demo
                            </Badge>
                        </div>
                    </CardHeader>
                    <CardContent>
                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                            <Pillar
                                icon={School}
                                title="교육특구 논지"
                                desc="대치1동 학군 선호(대치초·대청·숙명·단대 등)와 대장 단지 특성을 ‘탐색’ 화면에서 즉시 파악합니다."
                            />
                            <Pillar
                                icon={Wand2}
                                title="AI 자동매칭"
                                desc="수요자(예약) → AI 저평가 추천 → 상담/방문 → 계약 매칭까지 ‘전환 흐름’이 끊기지 않게 설계합니다."
                            />
                            <Pillar
                                icon={Share2}
                                title="AI 자동홍보"
                                desc="숏츠/3D투어 기반 콘텐츠를 자동 생성해 네이버·카카오·SNS로 확산, 계약 전환율을 끌어올립니다."
                            />
                        </div>
                        <Separator className="my-4" />
                        <div className="flex flex-col sm:flex-row gap-2 sm:items-center sm:justify-between">
                            <div className="text-sm text-muted-foreground">
                                {BRAND.officeName} · 대표 {BRAND.ceoName}
                            </div>
                            <div className="flex gap-2">
                                <Button className="rounded-xl" onClick={() => (window.location.hash = "#contact")}
                                >
                                    <Phone className="h-4 w-4 mr-2" /> 상담 연결
                                </Button>
                                <Button variant="outline" className="rounded-xl" onClick={() => (window.location.hash = "#about")}
                                >
                                    <ArrowRight className="h-4 w-4 mr-2" /> 앱 소개
                                </Button>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                <Card className="rounded-2xl shadow-sm md:col-span-5 overflow-hidden">
                    <div className="grid grid-cols-2 gap-2 p-3">
                        <div className="rounded-2xl border overflow-hidden aspect-[4/5] bg-muted">
                            <img
                                src={BRAND.assets.ceo}
                                alt="CEO"
                                className="w-full h-full object-cover"
                                onError={(e) => {
                                    (e.currentTarget as HTMLImageElement).style.display = "none";
                                }}
                            />
                            <div className="p-3 text-xs text-muted-foreground">CEO 사진 (assets에 넣으면 표시)</div>
                        </div>
                        <div className="rounded-2xl border overflow-hidden aspect-[4/5] bg-muted">
                            <img
                                src={BRAND.assets.businessCard}
                                alt="Business Card"
                                className="w-full h-full object-cover"
                                onError={(e) => {
                                    (e.currentTarget as HTMLImageElement).style.display = "none";
                                }}
                            />
                            <div className="p-3 text-xs text-muted-foreground">명함 (assets에 넣으면 표시)</div>
                        </div>
                    </div>
                    <div className="px-4 pb-4">
                        <div className="text-sm font-semibold">대표 인사말</div>
                        <p className="mt-1 text-sm text-muted-foreground leading-relaxed" id="about">
                            안녕하세요. {BRAND.officeName} 대표 {BRAND.ceoName}입니다.\n
                            대치1동은 ‘학군’이 곧 ‘주거 선택’이 되는 교육특구입니다.\n
                            저희는 이 국지적 특성을 정확히 구조화하고, AI가 저평가 매물을 빠르게 추천·예약·계약 매칭까지 연결하며,\n              숏츠 기반 자동홍보로 수요/공급을 촘촘히 연결해 계약 전환을 극대화합니다.
                        </p>
                        <div className="mt-3 flex flex-wrap gap-2">
                            <Badge variant="outline" className="rounded-xl">
                                <CheckCircle2 className="h-3.5 w-3.5 mr-1" /> 교육특구 특화
                            </Badge>
                            <Badge variant="outline" className="rounded-xl">
                                <CheckCircle2 className="h-3.5 w-3.5 mr-1" /> AI 저평가 추천
                            </Badge>
                            <Badge variant="outline" className="rounded-xl">
                                <CheckCircle2 className="h-3.5 w-3.5 mr-1" /> 자동홍보 숏츠
                            </Badge>
                        </div>
                    </div>
                </Card>
            </div>
        </div>
    );
}

function RegionInfo() {
    return (
        <div className="mx-auto max-w-6xl px-3 md:px-6 py-6">
            <div className="flex items-center gap-2 mb-3">
                <Home className="h-5 w-5" />
                <div>
                    <div className="font-semibold">대치1동 특성 · 교육환경</div>
                    <div className="text-sm text-muted-foreground">
                        왜 ‘대치1동’으로 이사하는가? 학군 선호 흐름을 한 화면에.
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
                <Card className="rounded-2xl shadow-sm md:col-span-7">
                    <CardHeader className="pb-2">
                        <CardTitle className="text-base">학군 선호 라인(요약)</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                        {SCHOOL_ROUTES.map((r) => (
                            <div key={r.id} className="rounded-2xl border p-3">
                                <div className="flex items-start justify-between gap-3">
                                    <div className="min-w-0">
                                        <div className="font-semibold truncate">{r.title}</div>
                                        <div className="text-sm text-muted-foreground mt-1">{r.line}</div>
                                    </div>
                                    <div className="flex gap-1 shrink-0">
                                        {r.tags.map((t) => (
                                            <Badge key={t} variant="secondary" className="rounded-xl">
                                                {t}
                                            </Badge>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        ))}
                        <div className="text-xs text-muted-foreground leading-relaxed">
                            * 이 데모는 구조/가독성 확인용입니다. 실제 학교·단지 좌표/라인 시각화는 지도 데이터(좌표) 연결 시 자동 렌더링됩니다.
                        </div>
                    </CardContent>
                </Card>

                <Card className="rounded-2xl shadow-sm md:col-span-5">
                    <CardHeader className="pb-2">
                        <CardTitle className="text-base">핵심 메시지(한 줄)</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                        <div className="rounded-2xl border p-3">
                            <div className="text-sm font-semibold">대치1동은 ‘학군’이 주거 선택을 결정합니다.</div>
                            <div className="text-sm text-muted-foreground mt-1">
                                따라서 단지별 전입 시나리오(초·중·고 라인)가 명확히 보이는 안내가 앱의 1번 핵심입니다.
                            </div>
                        </div>
                        <div className="rounded-2xl border p-3">
                            <div className="flex items-center gap-2 text-sm font-semibold">
                                <MapPin className="h-4 w-4" /> 다음 단계
                            </div>
                            <div className="text-sm text-muted-foreground mt-1">
                                이 화면에서 관심 단지를 선택하면, <b>추천매물</b>에서 AI가 저평가 매물만 선별해 보여주도록 연결합니다.
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}

function Recommend() {
    const [q, setQ] = useState("");
    const [onlyUndervalued, setOnlyUndervalued] = useState(true);

    const list = useMemo(() => {
        const base = SAMPLE_PROPERTIES.filter((p) =>
            (p.name + p.type + p.theme).toLowerCase().includes(q.toLowerCase())
        );
        return onlyUndervalued ? base.filter((p) => p.undervalued) : base;
    }, [q, onlyUndervalued]);

    return (
        <div className="mx-auto max-w-6xl px-3 md:px-6 py-6">
            <div className="flex items-center gap-2 mb-3">
                <Sparkles className="h-5 w-5" />
                <div>
                    <div className="font-semibold">AI 추천매물</div>
                    <div className="text-sm text-muted-foreground">저평가 신호 중심으로 ‘바로 예약 가능한’ 매물만 빠르게.</div>
                </div>
            </div>

            <div className="flex flex-col md:flex-row gap-2 md:items-center md:justify-between mb-4">
                <div className="flex gap-2 items-center">
                    <div className="relative w-full md:w-[360px]">
                        <Search className="h-4 w-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
                        <Input
                            className="pl-9 rounded-xl"
                            placeholder="단지/테마 검색 (예: 래미안, 은마, VIP)"
                            value={q}
                            onChange={(e) => setQ(e.target.value)}
                        />
                    </div>
                    <div className="flex items-center gap-2 px-3 py-2 rounded-xl border">
                        <span className="text-sm">저평가만</span>
                        <Switch checked={onlyUndervalued} onCheckedChange={setOnlyUndervalued} />
                    </div>
                </div>

                <Dialog>
                    <DialogTrigger asChild>
                        <Button variant="outline" className="rounded-xl">
                            <Sparkles className="h-4 w-4 mr-2" /> 추천 기준 보기
                        </Button>
                    </DialogTrigger>
                    <DialogContent className="rounded-2xl">
                        <DialogHeader>
                            <DialogTitle>AI 저평가 추천 기준(데모)</DialogTitle>
                        </DialogHeader>
                        <div className="text-sm text-muted-foreground leading-relaxed space-y-2">
                            <div>• 학군 선호 적합도(대치1동 전입 시나리오)</div>
                            <div>• 호가/실거래/급매 플래그 기반 할인 신호</div>
                            <div>• 수요자 선호(자녀 성별/학년/예산/입주 시기)</div>
                            <div>• 리스크(권리/명도/대출/일정) 점검</div>
                            <div className="text-xs">* 실제 운영 시, 로컬 DB + 외부 데이터 연동으로 고도화</div>
                        </div>
                    </DialogContent>
                </Dialog>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {list.map((p) => (
                    <Card key={p.id} className="rounded-2xl shadow-sm">
                        <CardHeader className="pb-2">
                            <div className="flex items-start justify-between gap-3">
                                <div className="min-w-0">
                                    <div className="font-semibold truncate">{p.name}</div>
                                    <div className="text-sm text-muted-foreground">{p.type} · {p.theme}</div>
                                </div>
                                <Badge className="rounded-xl" variant={p.undervalued ? "default" : "secondary"}>
                                    AI 신호 {p.signal}
                                </Badge>
                            </div>
                        </CardHeader>
                        <CardContent>
                            <div className="rounded-2xl border p-3 text-sm text-muted-foreground">
                                {p.priceNote}
                            </div>
                            <div className="mt-3 flex gap-2">
                                <Button className="rounded-xl flex-1">
                                    <CalendarDays className="h-4 w-4 mr-2" /> {p.cta}
                                </Button>
                                <Button variant="outline" className="rounded-xl">
                                    <MessageSquare className="h-4 w-4 mr-2" /> 챗봇
                                </Button>
                            </div>
                        </CardContent>
                    </Card>
                ))}
            </div>
        </div>
    );
}

function AIMatching() {
    const [child, setChild] = useState("초등");
    const [gender, setGender] = useState("무관");
    const [budget, setBudget] = useState("30억+");

    return (
        <div className="mx-auto max-w-6xl px-3 md:px-6 py-6">
            <div className="flex items-center gap-2 mb-3">
                <Bot className="h-5 w-5" />
                <div>
                    <div className="font-semibold">AI 매칭 시그널 · AI 챗봇 (통합)</div>
                    <div className="text-sm text-muted-foreground">
                        ‘예약 리드’가 들어오면, 최적 매물을 추천하고 계약까지 빠르게 연결합니다.
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
                <Card className="rounded-2xl shadow-sm md:col-span-7">
                    <CardHeader className="pb-2">
                        <CardTitle className="text-base">수요자 조건 (데모 입력)</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                            <Select value={child} onValueChange={setChild}>
                                <SelectTrigger className="rounded-xl"><SelectValue placeholder="자녀" /></SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="초등">초등</SelectItem>
                                    <SelectItem value="중등">중등</SelectItem>
                                    <SelectItem value="고등">고등</SelectItem>
                                    <SelectItem value="무자녀">무자녀</SelectItem>
                                </SelectContent>
                            </Select>
                            <Select value={gender} onValueChange={setGender}>
                                <SelectTrigger className="rounded-xl"><SelectValue placeholder="성별" /></SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="무관">무관</SelectItem>
                                    <SelectItem value="남">남</SelectItem>
                                    <SelectItem value="여">여</SelectItem>
                                </SelectContent>
                            </Select>
                            <Select value={budget} onValueChange={setBudget}>
                                <SelectTrigger className="rounded-xl"><SelectValue placeholder="예산" /></SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="20억~30억">20억~30억</SelectItem>
                                    <SelectItem value="30억+">30억+</SelectItem>
                                    <SelectItem value="전월세">전월세</SelectItem>
                                    <SelectItem value="VIP">VIP</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>

                        <div className="rounded-2xl border p-3 text-sm">
                            <div className="font-semibold">AI 매칭 결과(설명형 데모)</div>
                            <div className="text-sm text-muted-foreground mt-1 leading-relaxed">
                                • {child} 자녀 · {gender} · {budget} 조건에서, 학군 라인 적합도가 높은 단지를 우선 추천합니다.\n
                                • 추천매물의 ‘AI 신호’가 높은 매물부터 예약 슬롯을 자동 배정합니다.\n
                                • 리스크(권리/명도/일정) 체크리스트를 자동 생성해 상담 품질을 표준화합니다.
                            </div>
                        </div>

                        <div className="flex gap-2">
                            <Button className="rounded-xl flex-1">
                                <Sparkles className="h-4 w-4 mr-2" /> 저평가 매물로 자동 추천
                            </Button>
                            <Button variant="outline" className="rounded-xl flex-1">
                                <MessageSquare className="h-4 w-4 mr-2" /> AI 챗봇 열기
                            </Button>
                        </div>
                    </CardContent>
                </Card>

                <Card className="rounded-2xl shadow-sm md:col-span-5">
                    <CardHeader className="pb-2">
                        <CardTitle className="text-base">계약 전환 플로우</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2 text-sm text-muted-foreground">
                        <div className="rounded-2xl border p-3">
                            <div className="font-semibold text-foreground">1) 리드(예약) 입력</div>
                            <div>수요자 조건 → 자동 분류(우선콜/자료발송/리타겟)</div>
                        </div>
                        <div className="rounded-2xl border p-3">
                            <div className="font-semibold text-foreground">2) AI 추천</div>
                            <div>대치1동 학군 적합도 + 저평가 신호 결합</div>
                        </div>
                        <div className="rounded-2xl border p-3">
                            <div className="font-semibold text-foreground">3) 계약 매칭</div>
                            <div>서류/특약/일정 체크리스트로 신속 진행</div>
                        </div>
                        <div className="rounded-2xl border p-3">
                            <div className="font-semibold text-foreground">4) 자동홍보 연동</div>
                            <div>숏츠 생성 → 네이버/카카오/SNS 배포</div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}

function Register() {
    const [mode, setMode] = useState < "demand" | "supply" > ("demand");

    return (
        <div className="mx-auto max-w-6xl px-3 md:px-6 py-6">
            <div className="flex items-center gap-2 mb-3">
                <ClipboardList className="h-5 w-5" />
                <div>
                    <div className="font-semibold">사전등록 매칭 (수요자 → 공급자)</div>
                    <div className="text-sm text-muted-foreground">
                        수요자(예약)가 먼저 보이고, 공급자는 뒤에서 등록하도록 흐름을 정리합니다.
                    </div>
                </div>
            </div>

            <Tabs value={mode} onValueChange={(v) => setMode(v as any)}>
                <TabsList className="rounded-2xl">
                    <TabsTrigger value="demand" className="rounded-xl">1) 수요자 등록</TabsTrigger>
                    <TabsTrigger value="supply" className="rounded-xl">2) 공급자 등록</TabsTrigger>
                </TabsList>
                <TabsContent value="demand" className="mt-4">
                    <Card className="rounded-2xl shadow-sm">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-base">수요자(예약) 등록</CardTitle>
                        </CardHeader>
                        <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-3">
                            <Input className="rounded-xl" placeholder="이름" />
                            <Input className="rounded-xl" placeholder="연락처" />
                            <Select defaultValue="대치1동">
                                <SelectTrigger className="rounded-xl"><SelectValue placeholder="희망 지역" /></SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="대치1동">대치1동</SelectItem>
                                    <SelectItem value="대치2동">대치2동</SelectItem>
                                    <SelectItem value="삼성동">삼성동</SelectItem>
                                </SelectContent>
                            </Select>
                            <Select defaultValue="학군">
                                <SelectTrigger className="rounded-xl"><SelectValue placeholder="우선 목적" /></SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="학군">학군</SelectItem>
                                    <SelectItem value="렌트">렌트</SelectItem>
                                    <SelectItem value="투자">투자(재건축)</SelectItem>
                                    <SelectItem value="VIP">VIP(프리미엄)</SelectItem>
                                </SelectContent>
                            </Select>
                            <Button className="rounded-xl md:col-span-2">
                                <CalendarDays className="h-4 w-4 mr-2" /> 예약 요청 제출
                            </Button>
                            <div className="text-xs text-muted-foreground md:col-span-2">
                                제출 즉시 AI가 추천매물/매칭으로 연결하고, 담당자에게 우선콜 라우팅하도록 설계됩니다.
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="supply" className="mt-4">
                    <Card className="rounded-2xl shadow-sm">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-base">공급자(매물) 등록</CardTitle>
                        </CardHeader>
                        <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-3">
                            <Input className="rounded-xl" placeholder="단지/물건명" />
                            <Select defaultValue="아파트">
                                <SelectTrigger className="rounded-xl"><SelectValue placeholder="유형" /></SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="아파트">아파트</SelectItem>
                                    <SelectItem value="오피스텔">오피스텔</SelectItem>
                                    <SelectItem value="재건축">재건축</SelectItem>
                                    <SelectItem value="프리미엄">프리미엄</SelectItem>
                                </SelectContent>
                            </Select>
                            <Input className="rounded-xl" placeholder="가격(예: 28억 / 전세 12억)" />
                            <Input className="rounded-xl" placeholder="입주 가능일" />
                            <Button className="rounded-xl md:col-span-2">
                                <CheckCircle2 className="h-4 w-4 mr-2" /> 등록 제출
                            </Button>
                            <div className="text-xs text-muted-foreground md:col-span-2">
                                제출 시, AI가 저평가 신호/홍보 숏츠 생성 플로우로 연결합니다.
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>
        </div>
    );
}

function Shorts() {
    const [title, setTitle] = useState("대치1동 대장 아파트 20초 브리핑");
    const [platform, setPlatform] = useState("YouTube Shorts");

    return (
        <div className="mx-auto max-w-6xl px-3 md:px-6 py-6">
            <div className="flex items-center gap-2 mb-3">
                <Video className="h-5 w-5" />
                <div>
                    <div className="font-semibold">AI 숏츠매물 (자동홍보)</div>
                    <div className="text-sm text-muted-foreground">
                        매물 1개 → 숏츠 스크립트/썸네일/배포 문구까지 자동 생성 (데모)
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
                <Card className="rounded-2xl shadow-sm md:col-span-6">
                    <CardHeader className="pb-2">
                        <CardTitle className="text-base">생성 옵션</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                        <Input className="rounded-xl" value={title} onChange={(e) => setTitle(e.target.value)} />
                        <Select value={platform} onValueChange={setPlatform}>
                            <SelectTrigger className="rounded-xl"><SelectValue placeholder="플랫폼" /></SelectTrigger>
                            <SelectContent>
                                <SelectItem value="YouTube Shorts">YouTube Shorts</SelectItem>
                                <SelectItem value="Naver">네이버 링크/블로그</SelectItem>
                                <SelectItem value="Kakao">카카오톡 채널/오픈채팅</SelectItem>
                                <SelectItem value="SNS">인스타/맘카페/커뮤니티</SelectItem>
                            </SelectContent>
                        </Select>
                        <Button className="rounded-xl">
                            <Wand2 className="h-4 w-4 mr-2" /> 숏츠 홍보팩 생성
                        </Button>
                        <div className="text-xs text-muted-foreground">
                            * 실제 구현 시 watermark: “{BRAND.watermark}” 자동 삽입
                        </div>
                    </CardContent>
                </Card>

                <Card className="rounded-2xl shadow-sm md:col-span-6">
                    <CardHeader className="pb-2">
                        <CardTitle className="text-base">출력(데모)</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                        <div className="rounded-2xl border p-3">
                            <div className="text-sm font-semibold">{platform}용 한 줄</div>
                            <div className="text-sm text-muted-foreground mt-1">
                                “{title} | 대치1동 학군·대장 단지 핵심만 20초 요약. 상담/예약은 앱에서!”
                            </div>
                        </div>
                        <div className="rounded-2xl border p-3">
                            <div className="text-sm font-semibold">숏츠 스크립트(20초)</div>
                            <div className="text-sm text-muted-foreground mt-1 leading-relaxed">
                                ① 오늘의 대치1동 매물 핵심 1줄\n
                                ② 학군/입지 포인트 2개\n
                                ③ AI 저평가 신호 + 예약 유도\n
                                ④ {BRAND.officeName} 연락처 안내
                            </div>
                        </div>
                        <div className="rounded-2xl border p-3">
                            <div className="text-sm font-semibold">배포 체크</div>
                            <div className="text-sm text-muted-foreground mt-1">
                                네이버 매물 상세 → 앱 링크 삽입 · 카카오 공유 버튼 · SNS 자동 포스팅(관리자)
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}

function AdminPanel() {
    return (
        <div className="mx-auto max-w-6xl px-3 md:px-6 py-6">
            <div className="flex items-center gap-2 mb-3">
                <Shield className="h-5 w-5" />
                <div>
                    <div className="font-semibold">관리자 전용</div>
                    <div className="text-sm text-muted-foreground">일반 수요/공급자에게는 숨김 처리됩니다.</div>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {ADMIN_MENU.map((m) => (
                    <Card key={m.key} className="rounded-2xl shadow-sm">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-base flex items-center gap-2">
                                <m.icon className="h-4 w-4" /> {m.label}
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="text-sm text-muted-foreground">
                            관리자만 접근 가능한 기능(리포트/배포/시스템 설정 등)을 이 영역으로 이동해 메뉴 혼란을 제거합니다.
                        </CardContent>
                    </Card>
                ))}
            </div>
        </div>
    );
}

function Footer() {
    return (
        <div className="border-t" id="contact">
            <div className="mx-auto max-w-6xl px-3 md:px-6 py-6">
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
                    <div>
                        <div className="font-semibold">{BRAND.officeName}</div>
                        <div className="text-sm text-muted-foreground">
                            대표 {BRAND.ceoName} · 등록번호 11680-2023-00078
                        </div>
                    </div>
                    <div className="flex flex-wrap gap-2">
                        <Button variant="outline" className="rounded-xl">
                            <Phone className="h-4 w-4 mr-2" /> {BRAND.phoneMain}
                        </Button>
                        <Button variant="outline" className="rounded-xl">
                            <Phone className="h-4 w-4 mr-2" /> {BRAND.phoneMobile}
                        </Button>
                    </div>
                </div>
                <div className="mt-3 text-xs text-muted-foreground">워터마크: {BRAND.watermark}</div>
            </div>
        </div>
    );
}

export default function DaechiAIDemoApp() {
    const { isAdmin, toggle } = useAdminGate();
    const [active, setActive] = useState(MENU.region.key);

    useEffect(() => {
        // URL에서 admin 메뉴가 선택되면 관리자 패널로
        if (active === "admin" && !isAdmin) setActive(MENU.region.key);
    }, [active, isAdmin]);

    return (
        <div className="min-h-screen bg-background text-foreground">
            <TopBar active={active} setActive={setActive} isAdmin={isAdmin} />

            {/* 관리자 토글은 데모 편의용: 실제 운영에선 로그인/권한으로 대체 */}
            <div className="mx-auto max-w-6xl px-3 md:px-6 pt-3">
                <div className="flex items-center justify-end gap-2 text-sm text-muted-foreground">
                    <Lock className="h-4 w-4" /> 관리자 모드
                    <Switch checked={isAdmin} onCheckedChange={toggle} />
                </div>
            </div>

            <Hero />

            {active === MENU.region.key && <RegionInfo />}
            {active === MENU.추천매물.key && <Recommend />}
            {active === MENU.ai.key && <AIMatching />}
            {active === MENU.register.key && <Register />}
            {active === MENU.shorts.key && <Shorts />}
            {active === "admin" && isAdmin && <AdminPanel />}

            <Footer />
        </div>
    );
}

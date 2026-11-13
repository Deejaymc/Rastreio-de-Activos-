import asyncio
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.models import Asset, Base, DeviceStatus, LocationEvent, User, UserRole
from app.services.auth import hash_password

settings = get_settings()


async def seed() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as session:
        # 1. Usuários
        admin = await session.scalar(select(User).where(User.email == "admin@rastreio.io"))
        if not admin:
            admin = User(
                id=str(uuid4()),
                full_name="Administrador da Plataforma",
                email="admin@rastreio.io",
                phone_number="+244900000000",
                phone_verified=True,
                role=UserRole.admin,
                password_hash=hash_password("admin123"),
            )
            session.add(admin)

        user1 = await session.scalar(select(User).where(User.phone_number == "+244923111222"))
        if not user1:
            user1 = User(
                id=str(uuid4()),
                full_name="João Silva (Condutor)",
                email="joao.silva@empresa.ao",
                phone_number="+244923111222",
                phone_verified=True,
                role=UserRole.user,
                password_hash=hash_password("user123"),
            )
            session.add(user1)

        user2 = await session.scalar(select(User).where(User.phone_number == "+244924333444"))
        if not user2:
            user2 = User(
                id=str(uuid4()),
                full_name="Marta Fernandes (Técnica Campo)",
                email="marta.fernandes@empresa.ao",
                phone_number="+244924333444",
                phone_verified=True,
                role=UserRole.user,
                password_hash=hash_password("user123"),
            )
            session.add(user2)

        await session.flush()

        # 2. Dispositivos (Smartphones + Equipamentos IoT)
        now = datetime.now(UTC)

        devices_data = [
            {
                "id": str(uuid4()),
                "user_id": user1.id,
                "name": "Samsung Galaxy S24 (João Silva)",
                "imei": "864210041234561",
                "phone_number": "+244923111222",
                "platform": "ANDROID",
                "model": "Galaxy S24 Ultra",
                "os_version": "Android 14",
                "app_version": "1.0.0",
                "battery_level": 92,
                "is_charging": False,
                "status": DeviceStatus.active,
                "device_type": "SMARTPHONE",
                "active": True,
                "last_seen_at": now - timedelta(minutes=2),
                "trail": [
                    (-8.8300, 13.2350, 45.0, 5.0),
                    (-8.8320, 13.2380, 52.0, 4.0),
                    (-8.8350, 13.2420, 48.0, 4.2),
                    (-8.8383, 13.2444, 38.0, 3.8),
                ],
            },
            {
                "id": str(uuid4()),
                "user_id": user2.id,
                "name": "Xiaomi 13T (Marta Fernandes)",
                "imei": "864210041234562",
                "phone_number": "+244924333444",
                "platform": "ANDROID",
                "model": "Xiaomi 13T Pro",
                "os_version": "Android 14",
                "app_version": "1.0.0",
                "battery_level": 64,
                "is_charging": True,
                "status": DeviceStatus.active,
                "device_type": "SMARTPHONE",
                "active": True,
                "last_seen_at": now - timedelta(minutes=5),
                "trail": [
                    (-8.8800, 13.2100, 20.0, 6.0),
                    (-8.8850, 13.2150, 30.0, 5.5),
                    (-8.8912, 13.2201, 15.0, 5.0),
                ],
            },
            {
                "id": str(uuid4()),
                "user_id": None,
                "name": "Camião Volvo FH - Frota 04 (OBD2)",
                "imei": "358912048172635",
                "mac_address": "AA:BB:CC:11:22:33",
                "platform": "TELTONIKA",
                "model": "FMB920 OBD2",
                "battery_level": 100,
                "is_charging": True,
                "status": DeviceStatus.active,
                "device_type": "VEHICLE",
                "active": True,
                "last_seen_at": now - timedelta(minutes=1),
                "trail": [
                    (-8.8100, 13.2800, 75.0, 2.5),
                    (-8.8150, 13.2850, 78.0, 2.5),
                    (-8.8200, 13.2920, 80.0, 2.0),
                    (-8.8250, 13.2980, 65.0, 2.2),
                ],
            },
            {
                "id": str(uuid4()),
                "user_id": None,
                "name": "Container Frigorífico C-102 (IoT Tag)",
                "imei": "354890123456789",
                "mac_address": "00:1B:44:AA:BB:CC",
                "cell_id": "10001",
                "platform": "QUECTEL",
                "model": "BG95-M3 Asset Tag",
                "battery_level": 78,
                "is_charging": False,
                "status": DeviceStatus.active,
                "device_type": "CARGO_TAG",
                "active": True,
                "last_seen_at": now - timedelta(minutes=15),
                "trail": [
                    (-8.8050, 13.2200, 0.0, 8.0),
                    (-8.8052, 13.2201, 0.0, 7.5),
                ],
            },
        ]

        for d in devices_data:
            existing_dev = await session.scalar(select(Asset).where(Asset.imei == d["imei"]))
            if not existing_dev:
                dev = Asset(
                    id=d["id"],
                    user_id=d["user_id"],
                    name=d["name"],
                    imei=d["imei"],
                    mac_address=d.get("mac_address"),
                    phone_number=d.get("phone_number"),
                    cell_id=d.get("cell_id"),
                    platform=d["platform"],
                    model=d["model"],
                    os_version=d.get("os_version"),
                    app_version=d.get("app_version"),
                    battery_level=d["battery_level"],
                    is_charging=d["is_charging"],
                    status=d["status"],
                    device_type=d["device_type"],
                    active=d["active"],
                    last_seen_at=d["last_seen_at"],
                )
                session.add(dev)
                await session.flush()

                # Adiciona trilha de localizações
                trail = d["trail"]
                for i, (lat, lon, spd, acc) in enumerate(trail):
                    point_time = now - timedelta(minutes=(len(trail) - i) * 3)
                    loc = LocationEvent(
                        device_id=dev.id,
                        latitude=lat,
                        longitude=lon,
                        speed=spd,
                        bearing=90.0 + (i * 10),
                        accuracy=acc,
                        altitude=30.0 + i,
                        source="GPS",
                        captured_at=point_time,
                    )
                    session.add(loc)

        await session.commit()
    await engine.dispose()
    print("Seed concluído com sucesso!")


if __name__ == "__main__":
    asyncio.run(seed())
